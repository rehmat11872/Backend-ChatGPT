from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.http import JsonResponse
from django.core.exceptions import ValidationError

from .services.file_parser import FileParser
from .services.prompt_builder import PromptBuilder
from .services.legal_ai_service import LegalAIService
from .schemas.legal_ai_chat_schema import legal_ai_chat_schema
from drf_spectacular.utils import extend_schema


@extend_schema(tags=["Legal AI Chat"])
@legal_ai_chat_schema
class LegalAIChatAgentView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        """
        Accepts:
          - message: required string
          - file: optional (PDF, DOCX, TXT)
        Returns: full AI response (no streaming)
        """
        message = request.data.get("message")
        if not message:
            return JsonResponse({"error": "Message is required."}, status=400)

        # Read optional files
        files = request.FILES.getlist("file") if "file" in request.FILES else []
        if len(files) > 5:
            return JsonResponse({"error": "You can upload up to 5 files only."}, status=400)

        # Extract text from uploaded files
        combined_text = ""
        try:
            for f in files:
                combined_text += FileParser(f).extract_text() + "\n\n"
        except ValidationError as e:
            return JsonResponse({"error": str(e)}, status=400)

        # Build GPT prompt and get response
        messages = PromptBuilder(message, combined_text).build()
        ai_client = LegalAIService()

        try:
            ai_response = ai_client.get_response(messages)
            return JsonResponse({"success": True, "response": ai_response})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
