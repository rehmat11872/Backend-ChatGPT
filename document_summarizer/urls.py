from django.urls import path
from .views import ProcessDocumentView

urlpatterns = [
    path('process/', ProcessDocumentView.as_view(), name='document_process'),
]