from django.urls import path
from . import views, views_vector, views_judge_analytics

urlpatterns = [
    path('document-summarizer/', views.document_summarizer, name='document_summarizer'),
    path('chat/', views.ai_chat, name='ai_chat'),
    # Vector-enabled endpoints
    path('document-summarizer-vector/', views_vector.document_summarizer_vector, name='document_summarizer_vector'),
    path('chat-vector/', views_vector.ai_chat_vector, name='ai_chat_vector'),
    # Judge Analytics endpoints
    path('judge-analytics/ingest/', views_judge_analytics.ingest_judge_data, name='ingest_judge_data'),
    path('judge-analytics/judges/', views_judge_analytics.get_judges_list, name='get_judges_list'),
    path('judge-analytics/judge/<str:judge_id>/', views_judge_analytics.get_judge_analytics, name='get_judge_analytics'),
    path('judge-analytics/search/', views_judge_analytics.search_judges, name='search_judges'),
    path('judge-analytics/courts/', views_judge_analytics.get_court_statistics, name='get_court_statistics'),
    path('judge-analytics/court/<str:court_name>/comparison/', views_judge_analytics.get_court_comparison, name='get_court_comparison'),
]