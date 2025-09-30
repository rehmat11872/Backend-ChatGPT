from django.urls import path
from . import views

urlpatterns = [
    path('document-summarizer/', views.document_summarizer, name='document_summarizer'),
    path('chat/', views.ai_chat, name='ai_chat'),
]