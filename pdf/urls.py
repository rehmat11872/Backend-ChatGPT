from django.urls import path
from .views import ProtectPDFView, DownloadProtectedPDFView, MergePDFView, CompressPDFView, SplitPDFView, PDFToImageConversionView

urlpatterns = [
    #protected_pdf
    path('protect_pdf/', ProtectPDFView.as_view(), name='protect_pdf'),
    path('download_protected_pdf/<int:pdf_id>/', DownloadProtectedPDFView.as_view(), name='download_protected_pdf'),

    #merge pdf
    path('merge_pdf/', MergePDFView.as_view(), name='merge_pdf'),
    #compress pdf
    path('compress_pdf/', CompressPDFView.as_view(), name='compress_pdf'),
    #split pdf
    path('split_pdf/', SplitPDFView.as_view(), name='split_pdf'),
    #pdf to image/jpg
    path('pdf_to_image/', PDFToImageConversionView.as_view(), name='pdf_to_image'),
]
