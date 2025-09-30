from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import openai
from django.conf import settings
import PyPDF2
from docx import Document
import io

@csrf_exempt
@require_http_methods(["POST"])
def document_summarizer(request):
    try:
        text_content = ''
        additional_context = ''
        
        print(f"Document summarizer called. Files: {list(request.FILES.keys())}")
        print(f"POST data: {list(request.POST.keys())}")
        
        # Handle file upload
        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            
            # Get additional context if provided
            if 'additional_context' in request.POST:
                additional_context = request.POST.get('additional_context', '')
            
            if uploaded_file.content_type == 'application/pdf':
                # Extract text from PDF
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
                for page in pdf_reader.pages:
                    text_content += page.extract_text()
            elif uploaded_file.content_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword']:
                # Extract text from DOCX
                doc = Document(io.BytesIO(uploaded_file.read()))
                for paragraph in doc.paragraphs:
                    text_content += paragraph.text + '\n'
            elif uploaded_file.content_type == 'text/plain':
                # Handle text files
                text_content = uploaded_file.read().decode('utf-8')
            else:
                return JsonResponse({'error': 'Unsupported file type'}, status=400)
        else:
            # Handle text input
            data = json.loads(request.body)
            text_content = data.get('text', '')
        
        if not text_content.strip():
            print("No text content extracted")
            return JsonResponse({'error': 'No text content extracted from file'}, status=400)
        
        print(f"Extracted text length: {len(text_content)}")
        
        # Check if API key is available
        if not settings.OPENAI_API_KEY:
            print("ERROR: OpenAI API key not found in settings")
            return JsonResponse({'error': 'OpenAI API key not configured'}, status=500)
        
        # OpenAI API call for IRAC summarization
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Prepare the prompt based on whether additional context is provided
        if additional_context:
            user_prompt = f"User request: {additional_context}\n\nDocument content:\n{text_content}"
            system_prompt = "You are a helpful AI legal assistant. Analyze the document based on the user's specific request and provide relevant insights."
        else:
            user_prompt = f"Please analyze this legal document and provide an IRAC format summary:\n\n{text_content}"
            system_prompt = "You are a legal expert specializing in IRAC (Issue, Rule, Application, Conclusion) format analysis. Analyze the provided legal document and create a structured summary following IRAC methodology."
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            max_tokens=1500,
            temperature=0.3
        )
        
        summary = response.choices[0].message.content
        
        return JsonResponse({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        print(f"ERROR in document_summarizer: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def ai_chat(request):
    try:
        data = json.loads(request.body)
        message = data.get('message', '')
        
        if not message.strip():
            return JsonResponse({'error': 'No message provided'}, status=400)
        
        # Check if API key is available
        if not settings.OPENAI_API_KEY:
            print("ERROR: OpenAI API key not found in settings")
            return JsonResponse({'error': 'OpenAI API key not configured'}, status=500)
        
        print(f"Using OpenAI API key: {settings.OPENAI_API_KEY[:20]}...")
        
        # OpenAI API call for chat
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI legal assistant. Provide accurate, professional responses about legal matters, document analysis, and legal research. Always maintain a professional tone and provide practical guidance."
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        return JsonResponse({
            'success': True,
            'response': ai_response
        })
        
    except Exception as e:
        print(f"ERROR in ai_chat: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return JsonResponse({'error': str(e)}, status=500)