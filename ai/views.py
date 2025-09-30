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
        all_text_content = []
        document_sources = []
        additional_context = ''
        
        # Get multi-tenant and query parameters
        query_mode = request.POST.get('query_mode', 'general')
        response_format = request.POST.get('response_format', 'standard')
        user_role = request.POST.get('user_role', 'lawyer')
        firm_name = request.POST.get('firm_name', 'Unknown Firm')
        
        print(f"Document summarizer called by {user_role} from {firm_name}")
        print(f"Query mode: {query_mode}, Response format: {response_format}")
        print(f"Files: {list(request.FILES.keys())}")
        
        # Handle multiple file uploads
        file_keys = [key for key in request.FILES.keys() if key.startswith('file_')]
        
        if file_keys:
            for file_key in file_keys:
                uploaded_file = request.FILES[file_key]
                print(f"Processing file: {uploaded_file.name}, type: {uploaded_file.content_type}")
                
                file_text = ''
                if uploaded_file.content_type == 'application/pdf':
                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
                    for page_num, page in enumerate(pdf_reader.pages, 1):
                        page_text = page.extract_text()
                        file_text += f"[Page {page_num}] {page_text}\n"
                elif uploaded_file.content_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword']:
                    doc = Document(io.BytesIO(uploaded_file.read()))
                    for paragraph in doc.paragraphs:
                        file_text += paragraph.text + '\n'
                elif uploaded_file.content_type == 'text/plain':
                    file_text = uploaded_file.read().decode('utf-8')
                else:
                    return JsonResponse({'error': f'Unsupported file type: {uploaded_file.content_type}'}, status=400)
                
                if file_text.strip():
                    all_text_content.append(file_text)
                    document_sources.append({
                        'name': uploaded_file.name,
                        'type': uploaded_file.content_type,
                        'size': uploaded_file.size
                    })
        else:
            # Handle single file or text input
            if 'file' in request.FILES:
                uploaded_file = request.FILES['file']
                file_text = ''
                if uploaded_file.content_type == 'application/pdf':
                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
                    for page_num, page in enumerate(pdf_reader.pages, 1):
                        page_text = page.extract_text()
                        file_text += f"[Page {page_num}] {page_text}\n"
                elif uploaded_file.content_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword']:
                    doc = Document(io.BytesIO(uploaded_file.read()))
                    for paragraph in doc.paragraphs:
                        file_text += paragraph.text + '\n'
                elif uploaded_file.content_type == 'text/plain':
                    file_text = uploaded_file.read().decode('utf-8')
                
                if file_text.strip():
                    all_text_content.append(file_text)
                    document_sources.append({
                        'name': uploaded_file.name,
                        'type': uploaded_file.content_type,
                        'size': uploaded_file.size
                    })
            else:
                try:
                    data = json.loads(request.body)
                    text_content = data.get('text', '')
                    if text_content.strip():
                        all_text_content.append(text_content)
                        document_sources.append({'name': 'Text Input', 'type': 'text/plain'})
                except:
                    return JsonResponse({'error': 'No file or text provided'}, status=400)
        
        # Get additional context
        if 'additional_context' in request.POST:
            additional_context = request.POST.get('additional_context', '')
        
        if not all_text_content:
            return JsonResponse({'error': 'No text content extracted from files'}, status=400)
        
        combined_text = '\n\n--- DOCUMENT SEPARATOR ---\n\n'.join(all_text_content)
        print(f"Total extracted text length: {len(combined_text)}")
        
        # Chunk text if too long (approximate token limit: 12000 tokens = ~48000 characters)
        max_chars = 45000
        if len(combined_text) > max_chars:
            print(f"Text too long ({len(combined_text)} chars), chunking...")
            # Take first chunk and add summary note
            combined_text = combined_text[:max_chars] + "\n\n[Note: Document truncated due to length. This analysis covers the first portion of the document(s).]"
        
        # Check API key
        if not settings.OPENAI_API_KEY:
            return JsonResponse({'error': 'OpenAI API key not configured'}, status=500)
        
        # Prepare prompts based on query mode and response format
        system_prompts = {
            'general': f"You are a helpful AI legal assistant for {firm_name}. Provide professional legal analysis.",
            'summarize': f"You are a legal expert specializing in document summarization for {firm_name}. Create comprehensive summaries.",
            'research': f"You are a legal research specialist for {firm_name}. Focus on finding relevant legal precedents and citations.",
            'analysis': f"You are a case analysis expert for {firm_name}. Provide detailed legal analysis with reasoning.",
            'contract': f"You are a contract review specialist for {firm_name}. Focus on terms, risks, and compliance issues.",
            'judge': f"You are a judicial analytics expert for {firm_name}. Analyze judicial patterns and tendencies."
        }
        
        format_instructions = {
            'standard': "Provide a clear, professional response.",
            'irac': "Structure your response using IRAC format (Issue, Rule, Application, Conclusion).",
            'bullet': "Present your analysis in bullet point format with clear headings.",
            'structured': "Provide a structured analysis with numbered sections and subsections."
        }
        
        # Build user prompt
        if additional_context:
            user_prompt = f"User request: {additional_context}\n\n"
        else:
            user_prompt = f"Please analyze the following legal document(s) using {query_mode} approach:\n\n"
        
        user_prompt += f"Documents to analyze:\n{combined_text}\n\n"
        user_prompt += f"Instructions: {format_instructions[response_format]}\n"
        user_prompt += "Please provide citations with document names and page numbers where applicable."
        
        # OpenAI API call
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": system_prompts.get(query_mode, system_prompts['general'])
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
        
        # Extract citations (basic implementation)
        citations = []
        for i, source in enumerate(document_sources):
            citations.append({
                'document_id': str(i + 1),
                'document': source['name'],
                'page': None,  # Would need more sophisticated parsing
                'snippet': summary[:100] + '...' if len(summary) > 100 else summary
            })
        
        # Calculate confidence score (basic implementation)
        confidence = 0.85 if len(all_text_content) > 0 else 0.5
        
        return JsonResponse({
            'success': True,
            'summary': summary,
            'citations': citations,
            'confidence': confidence,
            'documents_processed': len(document_sources),
            'query_mode': query_mode,
            'response_format': response_format,
            'firm_context': firm_name
        })
        
    except Exception as e:
        print(f"ERROR in document_summarizer: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def ai_chat(request):
    try:
        data = json.loads(request.body)
        message = data.get('message', '')
        query_mode = data.get('query_mode', 'general')
        response_format = data.get('response_format', 'standard')
        user_role = data.get('user_role', 'lawyer')
        firm_name = data.get('firm_name', 'Unknown Firm')
        conversation_context = data.get('conversation_context', [])
        available_documents = data.get('available_documents', [])
        
        if not message.strip():
            return JsonResponse({'error': 'No message provided'}, status=400)
        
        # Check if API key is available
        if not settings.OPENAI_API_KEY:
            return JsonResponse({'error': 'OpenAI API key not configured'}, status=500)
        
        # Prepare prompts based on query mode
        system_prompts = {
            'general': f"You are a helpful AI legal assistant for {firm_name}. Provide professional legal guidance to {user_role}s.",
            'summarize': f"You are a legal summarization expert for {firm_name}. Help {user_role}s create concise summaries.",
            'research': f"You are a legal research specialist for {firm_name}. Assist {user_role}s with legal research and precedents.",
            'analysis': f"You are a legal analysis expert for {firm_name}. Provide detailed case analysis to {user_role}s.",
            'contract': f"You are a contract review specialist for {firm_name}. Help {user_role}s review and analyze contracts.",
            'judge': f"You are a judicial analytics expert for {firm_name}. Provide insights on judicial patterns to {user_role}s."
        }
        
        format_instructions = {
            'standard': "Provide a clear, professional response.",
            'irac': "Structure your response using IRAC format when applicable.",
            'bullet': "Present your response in bullet point format.",
            'structured': "Provide a structured response with clear sections."
        }
        
        # Build enhanced message with context
        context_info = ""
        if available_documents:
            context_info += "\n\nAvailable documents in this conversation:\n"
            for doc in available_documents:
                context_info += f"- {doc['name']}: {doc['content'][:200]}...\n"
        
        if conversation_context:
            context_info += "\n\nRecent conversation context:\n"
            for ctx in conversation_context[-3:]:  # Last 3 interactions
                if ctx.get('type') == 'query':
                    context_info += f"Previous Q: {ctx['content'][:100]}...\n"
                    context_info += f"Previous A: {ctx['response'][:100]}...\n"
                else:
                    context_info += f"Document: {ctx['name']} processed\n"
        
        enhanced_message = f"{message}{context_info}\n\nPlease respond using {response_format} format: {format_instructions[response_format]}"
        if available_documents:
            enhanced_message += "\nIf relevant, cite specific documents from the available documents list."
        
        # OpenAI API call for chat
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": system_prompts.get(query_mode, system_prompts['general'])
                },
                {
                    "role": "user",
                    "content": enhanced_message
                }
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # Enhanced confidence calculation
        confidence = 0.8 if len(message) > 20 else 0.6
        if available_documents:
            confidence += 0.1  # Higher confidence with document context
        if conversation_context:
            confidence += 0.05  # Slight boost for conversation context
        confidence = min(confidence, 0.95)  # Cap at 95%
        
        # Generate citations from available documents
        citations = []
        if available_documents:
            for i, doc in enumerate(available_documents):
                if any(word in ai_response.lower() for word in doc['name'].lower().split()):
                    citations.append({
                        'document_id': str(i + 1),
                        'document': doc['name'],
                        'page': None,
                        'snippet': doc['content'][:150] + '...' if len(doc['content']) > 150 else doc['content']
                    })
        
        return JsonResponse({
            'success': True,
            'response': ai_response,
            'citations': citations,
            'confidence': confidence,
            'query_mode': query_mode,
            'response_format': response_format,
            'firm_context': firm_name,
            'context_used': len(available_documents) + len(conversation_context)
        })
        
    except Exception as e:
        print(f"ERROR in ai_chat: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)