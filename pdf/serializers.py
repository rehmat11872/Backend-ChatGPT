# serializers.py
from rest_framework import serializers
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from .models import OcrPdf, ProtectedPDF, MergedPDF, CompressedPDF, SplitPDF, PDFImageConversion, StampPdf, WordToPdfConversion, WordToPdf, OrganizedPdf, UnlockPdf, PDFFormatConversion


class ProtectPDFRequestSerializer(serializers.Serializer):
    input_pdf = serializers.FileField(required=True)
    pdf_password = serializers.CharField(required=True)
    allow_printing = serializers.BooleanField(default=True)
    allow_copying = serializers.BooleanField(default=True)
    allow_editing = serializers.BooleanField(default=False)
    allow_comments = serializers.BooleanField(default=True)
    allow_form_filling = serializers.BooleanField(default=True)
    allow_document_assembly = serializers.BooleanField(default=False)


class MergePDFRequestSerializer(serializers.Serializer):
    pdf_files = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=False,
        help_text='Upload multiple PDF files with the same field name pdf_files.'
    )


class CompressPDFRequestSerializer(serializers.Serializer):
    input_pdf = serializers.FileField(required=True)
    compression_quality = serializers.ChoiceField(
        choices=[('extreme', 'extreme'), ('recommended', 'recommended'), ('less', 'less')],
        default='recommended'
    )


class SplitPDFRequestSerializer(serializers.Serializer):
    """Split PDF with three modes: Range, Pages, or Size. Only fill fields for your selected mode."""
    
    input_pdf = serializers.FileField(required=True)
    split_mode = serializers.ChoiceField(
        choices=[('range', 'Range'), ('pages', 'Pages'), ('size', 'Size')],
        default='range',
        help_text='Choose your split method'
    )
    
    # === RANGE MODE FIELDS (only use if split_mode = 'range') ===
    range_mode = serializers.ChoiceField(
        choices=[('custom', 'Custom ranges'), ('fixed', 'Fixed ranges')],
        required=False,
        help_text='RANGE MODE: How to define page ranges'
    )
    ranges = serializers.CharField(
        required=False,
        help_text='RANGE MODE: JSON like [{"from": 1, "to": 5}, {"from": 8, "to": 10}]'
    )
    merge_ranges = serializers.BooleanField(
        required=False, 
        default=False,
        help_text='RANGE MODE: Merge all ranges into one file'
    )
    
    # === PAGES MODE FIELDS (only use if split_mode = 'pages') ===
    extract_mode = serializers.ChoiceField(
        choices=[('all', 'Extract all pages'), ('select', 'Select pages')],
        required=False,
        help_text='PAGES MODE: Extract all pages or select specific ones'
    )
    pages_to_extract = serializers.CharField(
        required=False,
        help_text='PAGES MODE: Pages like "1,3-5,8" (only needed if extract_mode=select)'
    )
    merge_extracted = serializers.BooleanField(
        required=False, 
        default=False,
        help_text='PAGES MODE: Merge extracted pages into one file'
    )
    
    # === SIZE MODE FIELDS (only use if split_mode = 'size') ===
    max_file_size = serializers.IntegerField(
        required=False,
        help_text='SIZE MODE: Maximum size per split file'
    )
    size_unit = serializers.ChoiceField(
        choices=[('KB', 'KB'), ('MB', 'MB')],
        required=False,
        default='KB',
        help_text='SIZE MODE: Unit for max_file_size'
    )
    
    def validate(self, data):
        split_mode = data.get('split_mode', 'range')
        
        if split_mode == 'range':
            if not data.get('ranges'):
                raise serializers.ValidationError("For range mode: 'ranges' field is required")
        elif split_mode == 'pages':
            if data.get('extract_mode') == 'select' and not data.get('pages_to_extract'):
                raise serializers.ValidationError("For pages mode with 'select': 'pages_to_extract' field is required")
        elif split_mode == 'size':
            if not data.get('max_file_size'):
                raise serializers.ValidationError("For size mode: 'max_file_size' field is required")
        
        return data


class PDFToImageRequestSerializer(serializers.Serializer):
    input_pdf = serializers.FileField(required=True)


class WordToPdfRequestSerializer(serializers.Serializer):
    input_file = serializers.FileField(required=True)


class OrganizePDFRequestSerializer(serializers.Serializer):
    input_pdf = serializers.FileField(required=True)
    user_order = serializers.CharField(required=False, help_text='Order list as a string, e.g. [3,2,1]')
    delete_pages = serializers.CharField(required=False, help_text='Pages to delete as a string, e.g. [2,4,5]')


class UnlockPDFRequestSerializer(serializers.Serializer):
    input_pdf = serializers.FileField(required=True)
    password = serializers.CharField(required=True)


class StampPDFRequestSerializer(serializers.Serializer):
    input_pdf = serializers.FileField(required=True)
    text = serializers.CharField(required=True)


class OcrPDFRequestSerializer(serializers.Serializer):
    input_pdf = serializers.FileField(required=True)
    language = serializers.ChoiceField(
        choices=[
            ('eng', 'English'),
            ('spa', 'Spanish'),
            ('fra', 'French'),
            ('deu', 'German'),
        ],
        default='eng',
        help_text='Language for OCR text recognition'
    )


class PDFToFormatRequestSerializer(serializers.Serializer):
    input_pdf = serializers.FileField(required=True)
    output_format = serializers.ChoiceField(
        choices=[
            ('word', 'Word Document'),
            ('excel', 'Excel Spreadsheet'),
            ('powerpoint', 'PowerPoint'),
            ('jpeg', 'JPEG Images'),
            ('png', 'PNG Images'),
            ('text', 'Plain Text')
        ],
        required=True
    )


class ProtectedPDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProtectedPDF
        fields = '__all__'


class MergedPDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = MergedPDF
        fields = '__all__'


class CompressedPDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompressedPDF
        fields = '__all__'


class SplitPDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = SplitPDF
        fields = '__all__'


class PDFImageConversionSerializer(serializers.ModelSerializer):
    zip_file = serializers.SerializerMethodField()
    
    class Meta:
        model = PDFImageConversion
        fields = ['id', 'user', 'created_at', 'zip_file']
    
    def get_zip_file(self, obj):
        request = self.context.get('request')
        if request and obj.zip_file:
            protocol = 'https' if request.is_secure() else 'http'
            return f'{protocol}://{request.get_host()}{obj.zip_file.url}'
        return None


class WordToPdfSerializer(serializers.ModelSerializer):
    word_to_pdf = serializers.SerializerMethodField()

    class Meta:
        model = WordToPdf
        fields = ['word_to_pdf']

    def get_word_to_pdf(self, obj):
        request = self.context.get('request')
        if request and obj.word_to_pdf:
            protocol = 'https' if request.is_secure() else 'http'
            return f'{protocol}://{request.get_host()}{obj.word_to_pdf.url}'
        return None


class WordToPdfConversionSerializer(serializers.ModelSerializer):
    word_to_pdfs = WordToPdfSerializer(many=True)

    class Meta:
        model = WordToPdfConversion
        fields = ['id', 'user', 'word_to_pdfs', 'created_at']


class OrganizedPdfSerializer(serializers.ModelSerializer):
    organize_pdf = serializers.SerializerMethodField()
    
    class Meta:
        model = OrganizedPdf
        fields = ['id', 'user', 'organize_pdf', 'created_at']

    def get_organize_pdf(self, obj):
        request = self.context.get('request')
        if request and obj.organize_pdf:
            protocol = 'https' if request.is_secure() else 'http'
            return f'{protocol}://{request.get_host()}{obj.organize_pdf.url}'
        return None


class UnlockPdfSerializer(serializers.ModelSerializer):
    unlock_pdf = serializers.SerializerMethodField()
    
    class Meta:
        model = UnlockPdf
        fields = ['id', 'user', 'unlock_pdf', 'created_at']

    def get_unlock_pdf(self, obj):
        request = self.context.get('request')
        if request and obj.unlock_pdf:
            protocol = 'https' if request.is_secure() else 'http'
            return f'{protocol}://{request.get_host()}{obj.unlock_pdf.url}'
        return None


class StampPdfSerializer(serializers.ModelSerializer):
    pdf = serializers.SerializerMethodField()
    
    class Meta:
        model = StampPdf
        fields = ['id', 'user', 'pdf', 'created_at']

    def get_pdf(self, obj):
        request = self.context.get('request')
        if request and obj.pdf:
            protocol = 'https' if request.is_secure() else 'http'
            return f'{protocol}://{request.get_host()}{obj.pdf.url}'
        return None


class OcrPdfSerializer(serializers.ModelSerializer):
    pdf = serializers.SerializerMethodField()
    
    class Meta:
        model = OcrPdf
        fields = ['id', 'user', 'language', 'pdf', 'created_at']

    def get_pdf(self, obj):
        request = self.context.get('request')
        if request and obj.pdf:
            protocol = 'https' if request.is_secure() else 'http'
            return f'{protocol}://{request.get_host()}{obj.pdf.url}'
        return None


class PDFFormatConversionSerializer(serializers.ModelSerializer):
    converted_file = serializers.SerializerMethodField()
    
    class Meta:
        model = PDFFormatConversion
        fields = ['id', 'user', 'output_format', 'converted_file', 'created_at']
    
    def get_converted_file(self, obj):
        request = self.context.get('request')
        if request and obj.converted_file:
            protocol = 'https' if request.is_secure() else 'http'
            return f'{protocol}://{request.get_host()}{obj.converted_file.url}'
        return None