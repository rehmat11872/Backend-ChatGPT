from django.urls import path
from .views import DocumentUploadView, DocumentRetrieveView, DocumentTextExtractionView, DocumentSummarizeView

urlpatterns = [
    path('upload/', DocumentUploadView.as_view(), name='document_upload'),
    path('<int:document_id>/', DocumentRetrieveView.as_view(), name='document_retrieve'),
    path('<int:document_id>/extract/', DocumentTextExtractionView.as_view(), name='document_text_extract'),
    path('summarize/', DocumentSummarizeView.as_view(), name='document_summarize'),
]