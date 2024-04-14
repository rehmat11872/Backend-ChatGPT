from django.urls import path
from .views import PromptSubmissionViewSet


urlpatterns = [
    path('open_ai/', PromptSubmissionViewSet.as_view(), name='open_ai'),
    # path('open_ai/', PromptSubmissionViewSet.as_view(), name='open_ai'),
    # path('open_ai/<int:pk>/', PromptSubmissionViewSet.as_view({'put': 'update', 'delete': 'destroy'}), name='open_ai_detail'),
]
