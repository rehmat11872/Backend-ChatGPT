# serializers.py
from rest_framework import serializers
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site  
from .models import ProtectedPDF, MergedPDF, CompressedPDF, SplitPDF, PDFImageConversion, WordToPdfConversion, WordToPdf, OrganizedPdf, UnlockPdf

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
            base_url = f'https://{current_site.domain}'
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
            base_url = f'https://{current_site.domain}'
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
            base_url = f'https://{current_site.domain}'
            # base_url = f'http://{current_site.domain}'
            return f"{base_url}{settings.MEDIA_URL}{obj.organize_pdf.name}"
        return None
    