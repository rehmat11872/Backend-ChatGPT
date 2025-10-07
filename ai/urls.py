from django.urls import path
from . import views

urlpatterns = [
    path('document-summarizer/', views.document_summarizer, name='document_summarizer'),
    path('chat/', views.ai_chat, name='ai_chat'),
    path('chat-enhanced/', views.ai_chat, name='ai_chat_enhanced'),
    # Vector-enabled endpoints

    path('legal-chat/', views.legal_chat, name='legal_chat'),
]