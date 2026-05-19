import os
import sys
import time
import threading
import shutil
from datetime import datetime
from django.conf import settings

def get_train_root():
    p1 = os.path.join(settings.BASE_DIR, 'studio_django_utils', 'yolo', 'Train')
    p2 = os.path.join(settings.BASE_DIR, 'Train')
    root = p1 if os.path.isdir(p1) else p2
    if os.path.isdir(root) and root not in sys.path:
        sys.path.insert(0, root)
    return root

from ultralytics import YOLO
from .models import TrainingJob


RUNNING_JOBS = {}
CANCEL_FLAGS = {}


def _append_log(log_path: str, text: str):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(text + '\n')


def _resolve_paths(job: TrainingJob):
    base_dir = settings.BASE_DIR
    train_root = get_train_root()

    if job.model_family == 'v8':
        cfg = os.path.join(train_root, 'ultralytics', 'cfg', 'models', 'v8', 'yolov8.yaml')
        stem = 'yolov8'
    elif job.model_family == '11':
        cfg = os.path.join(train_root, 'ultralytics', 'cfg', 'models', '11', 'yolo11.yaml')
        stem = 'yolo11'
    elif job.model_family == '12':
        cfg = os.path.join(train_root, 'ultralytics', 'cfg', 'models', '12', 'yolo12.yaml')
        stem = 'yolo12'
    else:
        cfg = None
        stem = ''

    weight = None
    if job.model_size:
        candidate = os.path.join(train_root, 'pt', f'{stem}{job.model_size}.pt')
        if os.path.exists(candidate):
            weight = candidate

    dataset_yaml = job.dataset.data_yaml_path or ''
    if dataset_yaml:
        data_path = os.path.join(settings.MEDIA_ROOT, dataset_yaml)
    else:
        # 默认寻找data.yaml在数据集根目录
        data_path = os.path.join(settings.MEDIA_ROOT, job.dataset.root_folder_path, 'data.yaml')

    runs_dir = os.path.join(train_root, 'runs')
    job_name = f"{job.dataset.name}.v{job.dataset.version}"

    logs_path = os.path.join(settings.MEDIA_ROOT, 'yolo_train_logs', f'job_{job.id}.log')

    return cfg, weight, data_path, runs_dir, job_name, logs_path


def _register_callbacks(model, job: TrainingJob, logs_path: str):
    def on_train_start(trainer):
        _append_log(logs_path, f"[START] 开始训练 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def on_train_epoch_end(trainer):
        ep = trainer.epoch + 1 if hasattr(trainer, 'epoch') else 0
        total = trainer.epochs
        pct = int(ep * 100 / max(total, 1))
        job.progress = pct
        job.save(update_fields=['progress'])
        m = trainer.metrics or {}
        _append_log(logs_path, f"[EPOCH {ep}/{total}] metrics={m}")
        if CANCEL_FLAGS.get(job.id):
            raise KeyboardInterrupt('Canceled')

    def on_fit_epoch_end(trainer):
        # still record periodic metrics
        m = trainer.metrics or {}
        _append_log(logs_path, f"[METRICS] {m}")
        if CANCEL_FLAGS.get(job.id):
            raise KeyboardInterrupt('Canceled')

    def on_train_end(trainer):
        _append_log(logs_path, f"[END] 训练结束 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if CANCEL_FLAGS.get(job.id):
            job.status = 'canceled'
            job.finished_at = datetime.now()
            job.save(update_fields=['status', 'finished_at'])

    model.add_callback('on_train_start', on_train_start)
    model.add_callback('on_train_epoch_end', on_train_epoch_end)
    model.add_callback('on_fit_epoch_end', on_fit_epoch_end)
    model.add_callback('on_train_end', on_train_end)


def run_training(job_id: int):
    job = TrainingJob.objects.get(pk=job_id)
    cfg, weight, data_path, runs_dir, job_name, logs_path = _resolve_paths(job)
    job.logs_path = os.path.relpath(logs_path, settings.MEDIA_ROOT)
    job.status = 'running'
    job.started_at = datetime.now()
    job.save(update_fields=['logs_path', 'status', 'started_at'])

    try:
        _append_log(logs_path, f"使用配置: cfg={cfg}, weight={weight}, data={data_path}, project={runs_dir}, name={job_name}")

        model = YOLO(cfg)
        if weight:
            model.load(weight)

        _register_callbacks(model, job, logs_path)

        results = model.train(
            data=data_path,
            cache=False,
            imgsz=job.imgsz,
            epochs=job.epochs,
            single_cls=False,
            batch=job.batch,
            close_mosaic=0,
            workers=0,
            device=job.device,
            optimizer=job.optimizer,
            amp=True,
            project=runs_dir,
            name=job_name,
        )

        # 优先使用Ultralytics实际保存的目录，避免名称被自动加后缀导致不一致
        if hasattr(model, 'trainer') and getattr(model.trainer, 'save_dir', None):
            result_folder = str(model.trainer.save_dir)
        else:
            result_folder = os.path.join(runs_dir, job_name)
        source_yaml = data_path
        destination_yaml = os.path.join(result_folder, 'data.yaml')

        if CANCEL_FLAGS.get(job.id):
            job.runs_path = os.path.relpath(result_folder, settings.BASE_DIR) if os.path.exists(result_folder) else ''
            job.status = 'canceled'
            job.finished_at = datetime.now()
            job.save(update_fields=['runs_path', 'status', 'finished_at'])
        else:
            try:
                if os.path.exists(result_folder):
                    shutil.copy2(source_yaml, destination_yaml)
            except Exception as e:
                _append_log(logs_path, f"复制data.yaml失败: {str(e)}")

            best_path = os.path.join(result_folder, 'weights', 'best.pt')
            last_path = os.path.join(result_folder, 'weights', 'last.pt')

            job.runs_path = os.path.relpath(result_folder, settings.BASE_DIR)
            job.best_model_path = os.path.relpath(best_path, settings.BASE_DIR) if os.path.exists(best_path) else ''
            job.last_model_path = os.path.relpath(last_path, settings.BASE_DIR) if os.path.exists(last_path) else ''
            job.progress = 100
            job.status = 'completed'
            job.finished_at = datetime.now()
            job.save(update_fields=['runs_path', 'best_model_path', 'last_model_path', 'progress', 'status', 'finished_at'])

    except KeyboardInterrupt as e:
        _append_log(logs_path, f"[CANCELED] {str(e)}")
        job.status = 'canceled'
        job.error_message = str(e)
        job.finished_at = datetime.now()
        job.save(update_fields=['status', 'error_message', 'finished_at'])
    except Exception as e:
        _append_log(logs_path, f"[ERROR] {str(e)}")
        if CANCEL_FLAGS.get(job.id):
            job.status = 'canceled'
        else:
            job.status = 'failed'
        job.error_message = str(e)
        job.finished_at = datetime.now()
        job.save(update_fields=['status', 'error_message', 'finished_at'])
    finally:
        RUNNING_JOBS.pop(job.id, None)
        CANCEL_FLAGS.pop(job.id, None)


def start_job_async(job_id: int):
    t = threading.Thread(target=run_training, args=(job_id,), daemon=True)
    RUNNING_JOBS[job_id] = t
    t.start()


def cancel_job(job_id: int):
    CANCEL_FLAGS[job_id] = True
    try:
        job = TrainingJob.objects.get(pk=job_id)
        if job.status == 'queued':
            job.status = 'canceled'
            job.finished_at = datetime.now()
            job.save(update_fields=['status', 'finished_at'])
            CANCEL_FLAGS.pop(job_id, None)
            RUNNING_JOBS.pop(job_id, None)
        elif job.status == 'running':
            job.status = 'canceling'
            job.save(update_fields=['status'])
    except TrainingJob.DoesNotExist:
        pass