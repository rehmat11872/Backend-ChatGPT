from django.urls import path
from .views import *

urlpatterns = [
    #protected_pdf
    path('protect_pdf/', ProtectPDFView.as_view(), name='protect_pdf'),
    path('download_protected_pdf/<int:pdf_id>/', DownloadProtectedPDFView.as_view(), name='download_protected_pdf'),
    path('protect_pdf/delete/<int:pk>/', ProtectedPDFDeleteView.as_view(), name='protect_pdf_delete'),
    #merge pdf
    path('merge_pdf/', MergePDFView.as_view(), name='merge_pdf'),
    path('download_merged_pdf/<int:pdf_id>/', DownloadMergedPDFView.as_view(), name='download_merged_pdf'),
    path('merge_pdf/delete/<int:pk>/', MergePDFDeleteView.as_view(), name='merge_pdf_delete'),
    #compress pdf
    path('compress_pdf/', CompressPDFView.as_view(), name='compress_pdf'),
    path('download_compressed_pdf/<int:pdf_id>/', DownloadCompressedPDFView.as_view(), name='download_compressed_pdf'),
    path('compress_pdf/delete/<int:pk>/', CompressPDFDeleteView.as_view(), name='compress_pdf_delete'),

    #split pdf
    path('split_pdf/', SplitPDFView.as_view(), name='split_pdf'),
    path('download_split_pdf/<int:pdf_id>/', DownloadSplitPDFView.as_view(), name='download_split_pdf'),
    path('split_pdf/delete/<int:pk>/', SplitPDFDeleteView.as_view(), name='split_pdf_delete'),





    #organize pdf
    path('organize_pdf/', OrganizePDFView.as_view(), name='organize_pdf'),
    path('download_organized_pdf/<int:pdf_id>/', DownloadOrganizedPDFView.as_view(), name='download_organized_pdf'),
    #unlock_pdf
    path('unlock_pdf/', UnlockPDFView.as_view(), name='unlock_pdf'),
    path('download_unlocked_pdf/<int:pdf_id>/', DownloadUnlockedPDFView.as_view(), name='download_unlocked_pdf'),
    path('unlock_pdf/delete/<int:pk>/', UnlockPDFDeleteView.as_view(), name='unlock_pdf_delete'),

    #stamp pdf with text
    path('stamp_pdf_with_text/', StampPDFView.as_view(), name='stamp_pdf_with_text'),

    #sign pdf
    path('sign_pdf/', SignPDFView.as_view(), name='sign_pdf'),

    #OCR operations
    path('ocr_to_pdf/', OcrPDFView.as_view(), name='ocr_to_pdf'),
    path('download_ocr_pdf/<int:pdf_id>/', DownloadOcrPDFView.as_view(), name='download_ocr_pdf'),
    path('extract_text/', ExtractTextView.as_view(), name='extract_text'),
    
    #PDF to other formats
    path('pdf_to_format/', PDFToFormatView.as_view(), name='pdf_to_format'),
    path('download_format_converted/<int:conversion_id>/', DownloadFormatConvertedView.as_view(), name='download_format_converted'),
    
    #Other formats to PDF
    path('format_to_pdf/', FormatToPDFView.as_view(), name='format_to_pdf'),
    path('download_converted_pdf/<int:pdf_id>/', DownloadConvertedPDFView.as_view(), name='download_converted_pdf'),
    


]
