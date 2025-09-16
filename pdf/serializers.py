# serializers.py
from rest_framework import serializers
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from .models import OcrPdf, ProtectedPDF, MergedPDF, CompressedPDF, SplitPDF, PDFImageConversion, StampPdf, WordToPdfConversion, WordToPdf, OrganizedPdf, UnlockPdf


class ProtectPDFRequestSerializer(serializers.Serializer):
    input_pdf = serializers.FileField(required=True)
    pdf_password = serializers.CharField(required=True)


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
    input_pdf = serializers.FileField(required=True)
    start_page = serializers.IntegerField(required=True, min_value=1)
    end_page = serializers.IntegerField(required=True, min_value=1)


class PDFToImageRequestSerializer(serializers.Serializer):
    input_pdf = serializers.FileField(required=True)


class WordToPdfRequestSerializer(serializers.Serializer):
    input_file = serializers.FileField(required=True)


class OrganizePDFRequestSerializer(serializers.Serializer):
    input_pdf = serializers.FileField(required=True)
    user_order = serializers.CharField(help_text='Order list as a string, e.g. [3,2,1]')


class UnlockPDFRequestSerializer(serializers.Serializer):
    input_pdf = serializers.FileField(required=True)
    password = serializers.CharField(required=True)


class StampPDFRequestSerializer(serializers.Serializer):
    input_pdf = serializers.FileField(required=True)
    text = serializers.CharField(required=True)


class OcrPDFRequestSerializer(serializers.Serializer):
    input_pdf = serializers.FileField(required=True)

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
    class Meta:
        model = PDFImageConversion
        fields = ['id', 'user', 'created_at', 'zip_file']



class WordToPdfSerializer(serializers.ModelSerializer):
    word_to_pdf = serializers.SerializerMethodField()

    class Meta:
        model = WordToPdf
        fields = ['word_to_pdf']

    def get_word_to_pdf(self, obj):
        request = self.context.get('request')
        if request:
            current_site = get_current_site(request)
            base_url = f'http://{current_site.domain}'
            return f"{base_url}{settings.MEDIA_URL}{obj.word_to_pdf.name}"
        return None

class WordToPdfConversionSerializer(serializers.ModelSerializer):
    word_to_pdfs = WordToPdfSerializer(many=True)

    class Meta:
        model = WordToPdfConversion
        fields = ['id', 'user', 'word_to_pdfs', 'created_at']


class OrganizedPdfSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizedPdf
        fields = ['id', 'user',  'organize_pdf', 'created_at']

    def get_organize_pdf(self, obj):
        request = self.context.get('request')
        if request:
            current_site = get_current_site(request)
            base_url = f'http://{current_site.domain}'
            return f"{base_url}{settings.MEDIA_URL}{obj.organize_pdf.name}"
        return None


class UnlockPdfSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnlockPdf
        fields = ['id', 'user',  'unlock_pdf', 'created_at']

    def get_organize_pdf(self, obj):
        request = self.context.get('request')
        if request:
            current_site = get_current_site(request)
            base_url = f'http://{current_site.domain}'
            # base_url = f'http://{current_site.domain}'
            return f"{base_url}{settings.MEDIA_URL}{obj.organize_pdf.name}"
        return None

class StampPdfSerializer(serializers.ModelSerializer):
    class Meta:
        model = StampPdf
        fields = ['id', 'user',  'pdf', 'created_at']

    def get_pdf(self, obj):
        request = self.context.get('request')
        if request:
            current_site = get_current_site(request)
            base_url = f'http://{current_site.domain}'
            return f"{base_url}{settings.MEDIA_URL}{obj.organize_pdf.name}"
        return None

class OcrPdfSerializer(serializers.ModelSerializer):
    class Meta:
        model = OcrPdf
        fields = ['id', 'user',  'pdf', 'created_at']

    def get_pdf(self, obj):
        request = self.context.get('request')
        if request:
            current_site = get_current_site(request)
            base_url = f'http://{current_site.domain}'
            return f"{base_url}{settings.MEDIA_URL}{obj.organize_pdf.name}"
        return None
