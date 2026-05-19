import warnings
import shutil
import os

warnings.filterwarnings('ignore')
from ultralytics import YOLO

if __name__ == '__main__':
    # 数据集路径和项目配置
    dataset_name = "Car_Accident_Detection.v2i.yolov8"       # 数据集文件夹名称（保证放在Dataset文件夹下）

    dataset_path = os.path.join("Dataset", dataset_name, "data.yaml")        #数据集完整路径
    project_name = 'runs'   #训练结果输出文件夹
    # 模型配置
    model = YOLO('ultralytics/cfg/models/v8/yolov8.yaml')
    # 如何切换模型版本, 上面的ymal文件可以改为 yolov11s.yaml就是使用的v11s,
    # 类似某个改进的yaml文件名称为yolov11-XXX.yaml那么如果想使用其它版本就把上面的名称改为yolov11l-XXX.yaml即可（改的是上面YOLO中间的名字不是配置文件的）！
    model.load('pt/yolov8n.pt') # 是否加载预训练权重,科研不建议大家加载否则很难提升精度
    
    # 开始训练
    results = model.train(data=dataset_path,
                # 如果大家任务是其它的'ultralytics/cfg/default.yaml'找到这里修改task可以改成detect, segment, classify, pose
                cache=False,
                imgsz=640,
                epochs=100,
                single_cls=False,  # 是否是单类别检测
                batch=16,
                close_mosaic=0,
                workers=4,
                device='0',
                optimizer='SGD',  # using SGD 优化器 默认为auto建议大家使用固定的.
                # resume=, # 续训的话这里填写True, yaml文件的地方改为lats.pt的地址,需要注意的是如果你设置训练200轮次模型训练了200轮次是没有办法进行续训的.
                amp=True,  # 如果出现训练损失为Nan可以关闭amp
                project=project_name,
                name=dataset_name,
                )
    
    # 训练完成后，复制data.yaml文件到训练结果文件夹，方便导入系统使用
    try:
        # 构建训练结果文件夹路径
        result_folder = os.path.join(project_name, dataset_name)
        
        # 确保结果文件夹存在
        if os.path.exists(result_folder):
            # 复制data.yaml文件到结果文件夹
            source_yaml = dataset_path
            destination_yaml = os.path.join(result_folder, 'data.yaml')
            
            shutil.copy2(source_yaml, destination_yaml)
        else:
            print(f"训练结果文件夹不存在: {result_folder}")
            
    except Exception as e:
        print(f"复制 data.yaml 文件时出错: {str(e)}")
