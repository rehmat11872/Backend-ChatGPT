# serializers.py in your_app

from rest_framework import serializers
from .models import PromptSubmission
from drf_spectacular.utils import OpenApiExample

class PromptSubmissionRequestSerializer(serializers.Serializer):
    prompt = serializers.CharField()
    image = serializers.ImageField(required=False, allow_null=True, help_text='Optional JPEG image')

class PromptSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptSubmission
        fields = ['id', 'user', 'prompt', 'response', 'image']
        read_only_fields = ['user']


    def validate_image(self, value):
        # Check if the uploaded file is a JPEG image
        if value:
            if not value.name.lower().endswith('.jpg') and not value.name.lower().endswith('.jpeg'):
                raise serializers.ValidationError("Only JPEG images are allowed.")

        return value