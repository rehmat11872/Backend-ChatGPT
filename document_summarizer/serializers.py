from rest_framework import serializers
from .models import UploadedDocument

class DocumentUploadSerializer(serializers.Serializer):
    """Validates document upload requests"""
    document = serializers.FileField(required=True)
    
    def validate_document(self, value):
        # Check file extension
        allowed_extensions = ['.pdf', '.docx', '.txt']
        file_extension = value.name.lower().split('.')[-1]
        
        if f'.{file_extension}' not in allowed_extensions:
            raise serializers.ValidationError(
                f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Check file size (10MB limit)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 10MB")
            
        return value

class UploadedDocumentSerializer(serializers.ModelSerializer):
    """Serializes uploaded document metadata"""
    class Meta:
        model = UploadedDocument
        fields = ['id', 'file_name', 'file_type', 'file_size', 'created_at']

class TextExtractionSerializer(serializers.Serializer):
    """Serializes text extraction results"""
    text = serializers.CharField()
    word_count = serializers.IntegerField()
    truncated = serializers.BooleanField()

class SummarizeRequestSerializer(serializers.Serializer):
    """Validates summarization requests"""
    text = serializers.CharField(required=True)
    settings = serializers.DictField(required=False, default=dict)
    
    def validate_settings(self, value):
        # Validate format
        valid_formats = ['irac', 'executive', 'detailed', 'bullet_points']
        if 'format' in value and value['format'] not in valid_formats:
            raise serializers.ValidationError(f"Format must be one of: {valid_formats}")
        
        # Validate percentages
        for field in ['summary_length', 'confidence_threshold']:
            if field in value:
                if not isinstance(value[field], int) or not (0 <= value[field] <= 100):
                    raise serializers.ValidationError(f"{field} must be integer between 0-100")
        
        # Validate inclusions
        valid_inclusions = ['facts', 'issues', 'holdings', 'recs']
        if 'inclusions' in value:
            if not isinstance(value['inclusions'], list):
                raise serializers.ValidationError("inclusions must be a list")
            for item in value['inclusions']:
                if item not in valid_inclusions:
                    raise serializers.ValidationError(f"inclusions must be from: {valid_inclusions}")
        
        return value

class SummaryResponseSerializer(serializers.Serializer):
    """Serializes summary response with metadata"""
    summary = serializers.CharField()
    word_count = serializers.IntegerField()
    settings_used = serializers.DictField()
    truncated = serializers.BooleanField()
    tokens_used = serializers.IntegerField(allow_null=True)
    model = serializers.CharField()
    download_url = serializers.URLField()
    filename = serializers.CharField()
    file_size = serializers.IntegerField()
    document_id = serializers.IntegerField()