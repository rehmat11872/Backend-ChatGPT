from django.urls import path
from .views import LegalAIChatAgentView

urlpatterns = [
    path("legal/ai/chat/", LegalAIChatAgentView.as_view(), name="ai_chat"),
]
