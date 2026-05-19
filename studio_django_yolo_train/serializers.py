from rest_framework import serializers
from .models import TrainingJob
from studio_django_yolo.models import Dataset


class StartTrainingSerializer(serializers.Serializer):
    dataset_id = serializers.IntegerField()
    model_family = serializers.ChoiceField(choices=['v8', '11', '12'])
    model_size = serializers.ChoiceField(choices=['n', 's', 'm', 'l', 'x'], required=False, allow_blank=True)
    epochs = serializers.IntegerField(default=100, min_value=1, max_value=500)
    imgsz = serializers.IntegerField(default=640, min_value=64, max_value=2048)
    batch = serializers.IntegerField(default=16, min_value=1, max_value=256)
    device = serializers.CharField(default='0')
    optimizer = serializers.ChoiceField(choices=['SGD', 'Adam', 'AdamW', 'RMSProp'], default='SGD')

    def validate_dataset_id(self, value):
        try:
            Dataset.objects.get(pk=value)
            return value
        except Dataset.DoesNotExist:
            raise serializers.ValidationError('指定的数据集不存在')


class TrainingJobSerializer(serializers.ModelSerializer):
    dataset_name = serializers.CharField(source='dataset.name', read_only=True)

    class Meta:
        model = TrainingJob
        fields = [
            'id', 'dataset', 'dataset_name', 'model_family', 'model_size', 'weight_path', 'config_path',
            'status', 'logs_path', 'runs_path', 'best_model_path', 'last_model_path', 'progress',
            'epochs', 'imgsz', 'batch', 'device', 'optimizer', 'error_message',
            'created_at', 'started_at', 'finished_at'
        ]
        read_only_fields = ['status', 'logs_path', 'runs_path', 'best_model_path', 'last_model_path', 'progress',
                            'error_message', 'created_at', 'started_at', 'finished_at']