from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
    OpenApiRequest,
)

legal_ai_chat_schema = extend_schema(
    operation_id="LegalAIChat",
    description=(
        "Stream AI legal responses based on a text message and optional uploaded document "
        "(PDF, DOCX, or TXT). Max 5 files, 5 MB each, and 20 pages per PDF."
    ),
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "User's legal question or message (required).",
                },
                "file": {
                    "type": "array",
                    "items": {"type": "string", "format": "binary"},
                    "description": "Optional uploaded file(s): PDF, DOCX, or TXT.",
                },
            },
            "required": ["message"],
        }
    },
    responses={
        200: OpenApiResponse(description="Streamed AI response text (plain-text stream)."),
        400: OpenApiResponse(description="Validation error (file too large, missing message, etc.)."),
    },
    examples=[
        OpenApiExample(
            "Text only",
            summary="Ask a legal question without a file",
            description="Example POST message only",
            value={"message": "What is due process under U.S. law?"},
        ),
        OpenApiExample(
            "With file",
            summary="Ask a legal question with an attached PDF",
            description="Example POST message + PDF",
            value={"message": "Summarize this contract", "file": "<binary>"},
        ),
    ],
    tags=["Legal AI Chat"],
)
