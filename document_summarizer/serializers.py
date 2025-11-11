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
class ProcessDocumentSerializer(serializers.Serializer):
    """Validates document processing and settings requests"""
    action = serializers.ChoiceField(choices=['process', 'save', 'reset'], default='process')
    document = serializers.FileField(required=False)
    text = serializers.CharField(required=False)
    output_format = serializers.ChoiceField(choices=['irac', 'executive', 'detailed', 'bullet_points'], default='irac')
    summary_length = serializers.IntegerField(min_value=0, max_value=100, default=50)
    confidence_threshold = serializers.IntegerField(min_value=0, max_value=100, default=85)
    citation_style = serializers.ChoiceField(choices=['bluebook', 'apa', 'mla', 'chicago'], default='bluebook')
    language = serializers.ChoiceField(choices=['english', 'spanish', 'french', 'german'], default='english')
    auto_save = serializers.BooleanField(default=True)
    key_facts = serializers.BooleanField(default=True)
    legal_issues = serializers.BooleanField(default=True)
    holdings_and_rulings = serializers.BooleanField(default=True)
    recommendations = serializers.BooleanField(default=False)
    
    def validate(self, data):
        action = data.get('action', 'process')
        if action == 'process' and not data.get('document') and not data.get('text'):
            raise serializers.ValidationError("For 'process' action: Either 'document' file or 'text' must be provided")
        return data
class SettingsActionSerializer(serializers.Serializer):
    """Validates settings save/reset actions"""
    action = serializers.ChoiceField(choices=['save', 'reset'], required=True)
    
    # Settings fields (only required for save action)
    summary_length = serializers.IntegerField(min_value=0, max_value=100, required=False)
    confidence_threshold = serializers.IntegerField(min_value=0, max_value=100, required=False)
    key_facts = serializers.BooleanField(required=False)
    legal_issues = serializers.BooleanField(required=False)
    holdings_and_rulings = serializers.BooleanField(required=False)
    recommendations = serializers.BooleanField(required=False)
    citation_style = serializers.ChoiceField(choices=['bluebook', 'apa', 'mla', 'chicago'], required=False)
    language = serializers.ChoiceField(choices=['english', 'spanish', 'french', 'german'], required=False)
    auto_save = serializers.BooleanField(required=False)