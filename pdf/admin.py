from django.contrib import admin
from .models import ProtectedPDF, MergedPDF, CompressedPDF, SplitPDF, PDFImageConversion
# Register your models here.

class ProtectedPDFAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'password']  # Adjust the list of displayed fields as needed

admin.site.register(ProtectedPDF, ProtectedPDFAdmin)


class MergedPDFAdmin(admin.ModelAdmin):
    list_display = ['id', 'user']  # Adjust the list of displayed fields as needed

admin.site.register(MergedPDF, MergedPDFAdmin)




class CompressedPDFAdmin(admin.ModelAdmin):
    list_display = ['user', 'id']  

admin.site.register(CompressedPDF, CompressedPDFAdmin)

class SplitPDFAdmin(admin.ModelAdmin):
    list_display = ['user', 'id']  

admin.site.register(SplitPDF, SplitPDFAdmin)


class PDFImageConversionAdmin(admin.ModelAdmin):
    list_display = ['user', 'id']  

admin.site.register(PDFImageConversion, PDFImageConversionAdmin)