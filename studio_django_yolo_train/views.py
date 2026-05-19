import os
from django.conf import settings
from rest_framework.decorators import api_view
from studio_django_utils.responses.HertzResponse import HertzResponse
from .models import TrainingJob
from .serializers import StartTrainingSerializer, TrainingJobSerializer
from studio_django_yolo.models import Dataset
from .training_manager import start_job_async, get_train_root, cancel_job
import zipfile
import shutil


def _discover_versions():
    train_root = get_train_root()
    pt_dir = os.path.join(train_root, 'pt')
    weights = []
    if os.path.isdir(pt_dir):
        for f in os.listdir(pt_dir):
            if f.lower().endswith('.pt'):
                weights.append(f)

    families = []
    cfgs = {
        'v8': os.path.join(train_root, 'ultralytics', 'cfg', 'models', 'v8', 'yolov8.yaml'),
        '11': os.path.join(train_root, 'ultralytics', 'cfg', 'models', '11', 'yolo11.yaml'),
        '12': os.path.join(train_root, 'ultralytics', 'cfg', 'models', '12', 'yolo12.yaml'),
    }
    options = []
    for fam, cfg in cfgs.items():
        if os.path.exists(cfg):
            sizes = []
            stem = 'yolov8' if fam == 'v8' else f'yolo{fam}'
            for s in ['n', 's', 'm', 'l', 'x']:
                if f"{stem}{s}.pt" in weights:
                    sizes.append(s)
            options.append({'family': fam, 'config_path': cfg, 'sizes': sizes})
    return options


@api_view(['GET'])
def train_options(request):
    try:
        datasets = Dataset.objects.all().order_by('-created_at')
        ds = [{'id': d.id, 'name': d.name, 'version': d.version, 'yaml': d.data_yaml_path} for d in datasets]
        versions = _discover_versions()
        return HertzResponse.success(data={'datasets': ds, 'versions': versions}, message='获取训练选项成功')
    except Exception as e:
        return HertzResponse.error(message='获取训练选项失败', error=str(e))


@api_view(['POST'])
def start_training(request):
    try:
        serializer = StartTrainingSerializer(data=request.data)
        if not serializer.is_valid():
            return HertzResponse.validation_error(message='请求参数错误', errors=serializer.errors)

        v = serializer.validated_data
        dataset = Dataset.objects.get(pk=v['dataset_id'])

        train_root = get_train_root()
        config_map = {
            'v8': os.path.join(train_root, 'ultralytics', 'cfg', 'models', 'v8', 'yolov8.yaml'),
            '11': os.path.join(train_root, 'ultralytics', 'cfg', 'models', '11', 'yolo11.yaml'),
            '12': os.path.join(train_root, 'ultralytics', 'cfg', 'models', '12', 'yolo12.yaml'),
        }
        config_path = config_map.get(v['model_family'])

        job = TrainingJob.objects.create(
            dataset=dataset,
            model_family=v['model_family'],
            model_size=v.get('model_size') or '',
            config_path=os.path.relpath(config_path, settings.BASE_DIR),
            epochs=v['epochs'],
            imgsz=v['imgsz'],
            batch=v['batch'],
            device=v['device'],
            optimizer=v['optimizer'],
            status='queued',
            progress=0,
        )

        start_job_async(job.id)

        return HertzResponse.success(data=TrainingJobSerializer(job).data, message='训练任务创建成功')
    except Exception as e:
        return HertzResponse.error(message='创建训练任务失败', error=str(e))


@api_view(['GET'])
def job_detail(request, pk):
    try:
        job = TrainingJob.objects.get(pk=pk)
        return HertzResponse.success(data=TrainingJobSerializer(job).data, message='获取训练任务详情成功')
    except TrainingJob.DoesNotExist:
        return HertzResponse.not_found(message='训练任务不存在')
    except Exception as e:
        return HertzResponse.error(message='获取训练任务详情失败', error=str(e))


@api_view(['GET'])
def job_logs(request, pk):
    try:
        job = TrainingJob.objects.get(pk=pk)
        offset = int(request.GET.get('offset', '0') or '0')
        max_bytes = int(request.GET.get('max', '65536'))

        if not job.logs_path:
            return HertzResponse.success(data={'content': '', 'next_offset': 0, 'finished': job.status in ['completed', 'failed', 'canceled']}, message='日志为空')

        abs_log = os.path.join(settings.MEDIA_ROOT, job.logs_path)
        if not os.path.exists(abs_log):
            return HertzResponse.success(data={'content': '', 'next_offset': 0, 'finished': job.status in ['completed', 'failed', 'canceled']}, message='日志文件不存在')

        size = os.path.getsize(abs_log)
        if offset > size:
            offset = size

        with open(abs_log, 'rb') as f:
            f.seek(offset)
            chunk = f.read(max_bytes)
            next_offset = offset + len(chunk)
            content = chunk.decode('utf-8', errors='ignore')

        finished = job.status in ['completed', 'failed', 'canceled']
        return HertzResponse.success(data={'content': content, 'next_offset': next_offset, 'finished': finished}, message='获取日志成功')
    except TrainingJob.DoesNotExist:
        return HertzResponse.not_found(message='训练任务不存在')
    except Exception as e:
        return HertzResponse.error(message='获取训练日志失败', error=str(e))


@api_view(['GET'])
def jobs(request):
    try:
        qs = TrainingJob.objects.all().order_by('-created_at')
        return HertzResponse.success(data=TrainingJobSerializer(qs, many=True).data, message='获取训练任务列表成功')
    except Exception as e:
        return HertzResponse.error(message='获取训练任务列表失败', error=str(e))


@api_view(['POST'])
def cancel_training(request, pk):
    try:
        job = TrainingJob.objects.get(pk=pk)
        cancel_job(job.id)
        job.refresh_from_db()
        return HertzResponse.success(data=TrainingJobSerializer(job).data, message='训练任务取消已请求')
    except TrainingJob.DoesNotExist:
        return HertzResponse.not_found(message='训练任务不存在')
    except Exception as e:
        return HertzResponse.error(message='取消训练任务失败', error=str(e))


@api_view(['GET'])
def download_training(request, pk):
    try:
        job = TrainingJob.objects.get(pk=pk)
        if not job.runs_path:
            return HertzResponse.fail(message='训练输出不存在')
        run_dir = os.path.join(settings.BASE_DIR, job.runs_path)
        if not os.path.isdir(run_dir):
            return HertzResponse.fail(message='训练输出目录不存在')

        archive_root = os.path.join(settings.MEDIA_ROOT, 'yolo_train_archives')
        os.makedirs(archive_root, exist_ok=True)
        base_name = os.path.basename(run_dir)
        zip_path = os.path.join(archive_root, f'{base_name}.zip')

        with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(run_dir):
                for f in files:
                    fp = os.path.join(root, f)
                    arc = os.path.join(base_name, os.path.relpath(fp, run_dir))
                    zf.write(fp, arc)

        rel_url = os.path.join('yolo_train_archives', f'{base_name}.zip').replace('\\', '/')
        download_url = f"{settings.MEDIA_URL}{rel_url}"
        size = os.path.getsize(zip_path)
        return HertzResponse.success(data={'url': download_url, 'size': size}, message='训练文件打包成功')
    except TrainingJob.DoesNotExist:
        return HertzResponse.not_found(message='训练任务不存在')
    except Exception as e:
        return HertzResponse.error(message='训练文件打包失败', error=str(e))


@api_view(['POST'])
def delete_training(request, pk):
    try:
        job = TrainingJob.objects.get(pk=pk)
        if job.status in ['running', 'canceling']:
            return HertzResponse.fail(message='训练任务正在运行或取消中，请先取消并等待结束后再删除')

        # 删除训练输出目录
        if job.runs_path:
            run_dir = os.path.join(settings.BASE_DIR, job.runs_path)
            if os.path.isdir(run_dir):
                shutil.rmtree(run_dir, ignore_errors=True)

        # 删除日志文件
        if job.logs_path:
            log_file = os.path.join(settings.MEDIA_ROOT, job.logs_path)
            if os.path.exists(log_file):
                try:
                    os.remove(log_file)
                except Exception:
                    pass

        # 删除打包的zip
        base_name = os.path.basename(os.path.join(settings.BASE_DIR, job.runs_path)) if job.runs_path else None
        if base_name:
            zip_path = os.path.join(settings.MEDIA_ROOT, 'yolo_train_archives', f'{base_name}.zip')
            if os.path.exists(zip_path):
                try:
                    os.remove(zip_path)
                except Exception:
                    pass

        job.delete()
        return HertzResponse.success(message='训练任务删除成功')
    except TrainingJob.DoesNotExist:
        return HertzResponse.not_found(message='训练任务不存在')
    except Exception as e:
        return HertzResponse.error(message='删除训练任务失败', error=str(e))