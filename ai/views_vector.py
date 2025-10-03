from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import openai
from django.conf import settings
import PyPDF2
from docx import Document as DocxDocument
import io
from django.core.files.base import ContentFile
from .models import Document, DocumentChunk, VectorEmbedding, Conversation, ConversationMessage
from .vector_utils import VectorProcessor
from django.contrib.auth import get_user_model

User = get_user_model()

@csrf_exempt
@require_http_methods(["POST"])
def document_summarizer_vector(request):
    try:
        # Get parameters
        query_mode = request.POST.get('query_mode', 'general')
        response_format = request.POST.get('response_format', 'standard')
        user_role = request.POST.get('user_role', 'lawyer')
        firm_name = request.POST.get('firm_name', 'Unknown Firm')
        additional_context = request.POST.get('additional_context', '')
        
        # Get or create test user (in production, use request.user)
        user, _ = User.objects.get_or_create(email='test@example.com')
        
        # Initialize vector processor
        vector_processor = VectorProcessor()
        
        # Process uploaded files
        processed_documents = []
        file_keys = [key for key in request.FILES.keys() if key.startswith('file_')] or (['file'] if 'file' in request.FILES else [])
        
        for file_key in file_keys:
            uploaded_file = request.FILES[file_key]
            
            # Extract text from file
            file_text = ''
            total_pages = 0
            
            if uploaded_file.content_type == 'application/pdf':
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
                total_pages = len(pdf_reader.pages)
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    page_text = page.extract_text()
                    file_text += f"[Page {page_num}] {page_text}\n"
            elif uploaded_file.content_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword']:
                doc = DocxDocument(io.BytesIO(uploaded_file.read()))
                for paragraph in doc.paragraphs:
                    file_text += paragraph.text + '\n'
            elif uploaded_file.content_type == 'text/plain':
                file_text = uploaded_file.read().decode('utf-8')
            
            if not file_text.strip():
                continue
            
            # Save document metadata to database (no file storage until S3)
            document = Document.objects.create(
                user=user,
                title=uploaded_file.name,
                file_type=uploaded_file.content_type,
                file_size=uploaded_file.size,
                total_pages=total_pages
                # file_path will be empty until S3 setup
                # organization will be null for now until proper org setup
            )
            
            # Process and store chunks with embeddings
            chunks_created = vector_processor.store_document_chunks(document, file_text)
            print(f"Created {chunks_created} chunks for {uploaded_file.name}")
            
            processed_documents.append({
                'document': document,
                'text': file_text[:1000] + '...' if len(file_text) > 1000 else file_text
            })
        
        if not processed_documents:
            return JsonResponse({'error': 'No documents processed'}, status=400)
        
        # Use vector search to find relevant chunks
        query_text = additional_context if additional_context else f"Analyze using {query_mode} approach"
        document_ids = [doc['document'].id for doc in processed_documents]
        
        relevant_chunks = vector_processor.similarity_search(
            query_text=query_text,
            document_ids=document_ids,
            top_k=5
        )
        
        # Build context from relevant chunks
        context_text = '\n\n'.join([chunk['chunk'].chunk_text for chunk in relevant_chunks])
        
        # Generate AI response
        system_prompts = {
            'general': f"You are a helpful AI legal assistant for {firm_name}.",
            'summarize': f"You are a legal expert specializing in document summarization for {firm_name}.",
            'research': f"You are a legal research specialist for {firm_name}.",
            'analysis': f"You are a case analysis expert for {firm_name}.",
            'contract': f"You are a contract review specialist for {firm_name}.",
            'judge': f"You are a judicial analytics expert for {firm_name}."
        }
        
        format_instructions = {
            'standard': "Provide a clear, professional response.",
            'irac': "Structure your response using IRAC format.",
            'bullet': "Present your analysis in bullet point format.",
            'structured': "Provide a structured analysis with numbered sections."
        }
        
        user_prompt = f"{additional_context}\n\nRelevant document content:\n{context_text}\n\n{format_instructions[response_format]}"
        
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompts.get(query_mode, system_prompts['general'])},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1500,
            temperature=0.3
        )
        
        summary = response.choices[0].message.content
        
        # Generate citations from relevant chunks
        citations = []
        for chunk_data in relevant_chunks:
            citations.append({
                'document_id': str(chunk_data['document'].id),
                'document': chunk_data['document'].title,
                'page': chunk_data['chunk'].page_number,
                'snippet': chunk_data['chunk'].chunk_text[:150] + '...',
                'similarity': round(chunk_data['similarity'], 3)
            })
        
        return JsonResponse({
            'success': True,
            'summary': summary,
            'citations': citations,
            'confidence': 0.9,
            'documents_processed': len(processed_documents),
            'chunks_found': len(relevant_chunks),
            'query_mode': query_mode,
            'response_format': response_format
        })
        
    except Exception as e:
        print(f"ERROR in document_summarizer_vector: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def ai_chat_vector(request):
    try:
        data = json.loads(request.body)
        message = data.get('message', '')
        query_mode = data.get('query_mode', 'general')
        response_format = data.get('response_format', 'standard')
        user_role = data.get('user_role', 'lawyer')
        firm_name = data.get('firm_name', 'Unknown Firm')
        
        if not message.strip():
            return JsonResponse({'error': 'No message provided'}, status=400)
        
        # Get or create test user
        user, _ = User.objects.get_or_create(email='test@example.com')
        
        # Initialize vector processor
        vector_processor = VectorProcessor()
        
        # Get user's recent documents for context
        recent_docs = Document.objects.filter(user=user).order_by('-created_at')[:10]
        document_ids = [doc.id for doc in recent_docs]
        
        # Perform vector search across user's documents
        relevant_chunks = vector_processor.similarity_search(
            query_text=message,
            document_ids=document_ids,
            top_k=3
        )
        
        # Build context from relevant chunks
        context_info = ""
        if relevant_chunks:
            context_info = "\n\nRelevant information from your documents:\n"
            for chunk_data in relevant_chunks:
                context_info += f"From {chunk_data['document'].title}: {chunk_data['chunk'].chunk_text[:200]}...\n\n"
        
        # Generate AI response
        system_prompts = {
            'general': f"You are a helpful AI legal assistant for {firm_name}. Use provided document context when relevant.",
            'summarize': f"You are a legal summarization expert for {firm_name}.",
            'research': f"You are a legal research specialist for {firm_name}.",
            'analysis': f"You are a legal analysis expert for {firm_name}.",
            'contract': f"You are a contract review specialist for {firm_name}.",
            'judge': f"You are a judicial analytics expert for {firm_name}."
        }
        
        enhanced_message = f"{message}{context_info}"
        
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompts.get(query_mode, system_prompts['general'])},
                {"role": "user", "content": enhanced_message}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # Generate citations from relevant chunks
        citations = []
        for chunk_data in relevant_chunks:
            citations.append({
                'document_id': str(chunk_data['document'].id),
                'document': chunk_data['document'].title,
                'page': chunk_data['chunk'].page_number,
                'snippet': chunk_data['chunk'].chunk_text[:100] + '...',
                'similarity': round(chunk_data['similarity'], 3)
            })
        
        return JsonResponse({
            'success': True,
            'response': ai_response,
            'citations': citations,
            'confidence': 0.85,
            'context_used': len(relevant_chunks),
            'query_mode': query_mode,
            'response_format': response_format
        })
        
    except Exception as e:
        print(f"ERROR in ai_chat_vector: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)