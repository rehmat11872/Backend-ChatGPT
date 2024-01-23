# serializers.py
from rest_framework import serializers
from .models import ProtectedPDF, MergedPDF, CompressedPDF, SplitPDF

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