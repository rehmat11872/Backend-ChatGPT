from django.urls import path
from .views import *

urlpatterns = [
    #protected_pdf
    path('protect_pdf/', ProtectPDFView.as_view(), name='protect_pdf'),
    path('download_protected_pdf/<int:pdf_id>/', DownloadProtectedPDFView.as_view(), name='download_protected_pdf'),
    path('protect_pdf/delete/<int:pk>/', ProtectedPDFDeleteView.as_view(), name='protect_pdf_delete'),
    #merge pdf
    path('merge_pdf/', MergePDFView.as_view(), name='merge_pdf'),
    path('merge_pdf/delete/<int:pk>/', MergePDFDeleteView.as_view(), name='merge_pdf_delete'),
    #compress pdf
    path('compress_pdf/', CompressPDFView.as_view(), name='compress_pdf'),
    path('compress_pdf/delete/<int:pk>/', CompressPDFDeleteView.as_view(), name='compress_pdf_delete'),

    #split pdf
    path('split_pdf/', SplitPDFView.as_view(), name='split_pdf'),
    path('split_pdf/delete/<int:pk>/', SplitPDFDeleteView.as_view(), name='split_pdf_delete'),

    #pdf to image/jpg
    path('pdf_to_image/', PDFToImageConversionView.as_view(), name='pdf_to_image'),
    path('pdf_to_image/delete/<int:pk>/', PDFToImageDeleteView.as_view(), name='pdf_to_image_delete'),
    #word to pdf
    path('word_to_pdf/', WordToPdfConversionView.as_view(), name='word_to_pdf'),
    path('word_to_pdf/delete/<int:pk>/', WordToPdfConversionDeleteView.as_view(), name='word_to_pdf_delete'),


    #organize pdf
    path('organize_pdf/', OrganizePDFView.as_view(), name='organize_pdf'),
    #unlock_pdf
    path('unlock_pdf/', UnlockPDFView.as_view(), name='unlock_pdf'),
    path('unlock_pdf/delete/<int:pk>/', UnlockPDFDeleteView.as_view(), name='unlock_pdf_delete'),

    #stamp pdf with text
    path('stamp_pdf_with_text/', StampPDFView.as_view(), name='stamp_pdf_with_text'),

]
