import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema
from django.core.files.base import ContentFile
from .models import UploadedDocument
from .serializers import ProcessDocumentSerializer, SummaryResponseSerializer, SettingsActionSerializer
from .text_extractor import TextExtractor


@extend_schema(tags=['Document Summarizer'])
class ProcessDocumentView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    
    @extend_schema(
        request=ProcessDocumentSerializer,
        responses={200: SummaryResponseSerializer}
    )
    def post(self, request):
        serializer = ProcessDocumentSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        action = serializer.validated_data.get('action', 'process')
        
        try:
            if action == 'save':
                from .models import UserSettings
                user = request.user if request.user.is_authenticated else None
                if not user:
                    return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
                
                settings, created = UserSettings.objects.get_or_create(user=user)
                settings.summary_length = serializer.validated_data.get('summary_length', 60)
                settings.confidence_threshold = serializer.validated_data.get('confidence_threshold', 75)
                settings.key_facts = serializer.validated_data.get('key_facts', True)
                settings.legal_issues = serializer.validated_data.get('legal_issues', True)
                settings.holdings_and_rulings = serializer.validated_data.get('holdings_and_rulings', True)
                settings.recommendations = serializer.validated_data.get('recommendations', False)
                settings.citation_style = serializer.validated_data.get('citation_style', 'bluebook')
                settings.language = serializer.validated_data.get('language', 'english')
                settings.auto_save = serializer.validated_data.get('auto_save', True)
                settings.save()
                
                return Response({
                    'status': 'success',
                    'message': 'Settings saved successfully.'
                })
            
            elif action == 'reset':
                from .models import UserSettings
                user = request.user if request.user.is_authenticated else None
                if user:
                    UserSettings.objects.filter(user=user).delete()
                
                default_settings = {
                    'summary_length': 60,
                    'confidence_threshold': 75,
                    'key_facts': True,
                    'legal_issues': True,
                    'holdings_and_rulings': True,
                    'recommendations': False,
                    'citation_style': 'bluebook',
                    'language': 'english',
                    'auto_save': True
                }
                return Response({
                    'status': 'success',
                    'message': 'Settings reset to defaults.',
                    'default_settings': default_settings
                })
            
            elif action == 'process':
                # Extract text from document or use provided text
                if serializer.validated_data.get('document'):
                    document_file = serializer.validated_data['document']
                    file_extension = document_file.name.lower().split('.')[-1]
                    extracted_text = TextExtractor.extract_text(document_file, file_extension)
                else:
                    extracted_text = serializer.validated_data['text']
                
                # Build settings for AI prompt
                settings = {
                    'output_format': serializer.validated_data['output_format'],
                    'summary_length': serializer.validated_data['summary_length'],
                    'confidence_threshold': serializer.validated_data['confidence_threshold'],
                    'citation_style': serializer.validated_data['citation_style'],
                    'language': serializer.validated_data['language'],
                    'auto_save': serializer.validated_data['auto_save'],
                    'key_facts': serializer.validated_data['key_facts'],
                    'legal_issues': serializer.validated_data['legal_issues'],
                    'holdings_and_rulings': serializer.validated_data['holdings_and_rulings'],
                    'recommendations': serializer.validated_data['recommendations']
                }
                
                # Generate summary using your advanced prompt
                result = self._generate_advanced_summary(extracted_text, settings, request)
                return Response(result)
            
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': f'Request failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _generate_advanced_summary(self, document_text, settings, request):
        import datetime
        
        # Build advanced prompt template
        prompt = f"""You are an advanced AI Legal Document Summarizer.

Your task is to analyze and summarize a legal document based on the user's selected configuration and output format.

=========================
USER SETTINGS
=========================
Output Format: {settings['output_format']}                  // IRAC Format | Executive Summary | Detailed Analysis | Bullet Points
Summary Length: {settings['summary_length']}%               // 0–100; controls level of detail
Confidence Threshold: {settings['confidence_threshold']}%   // 0–100; affects certainty of analysis
Citation Style: {settings['citation_style']}                // Bluebook | APA | MLA | Chicago
Language: {settings['language']}                            // English | Spanish | French | German
Auto-Save: {settings['auto_save']}                          // true | false

=========================
CONTENT INCLUSIONS
=========================
Include Key Facts: {settings['key_facts']}                     // true | false
Include Legal Issues: {settings['legal_issues']}               // true | false
Include Holdings & Rulings: {settings['holdings_and_rulings']} // true | false
Include Recommendations: {settings['recommendations']}         // true | false

=========================
DOCUMENT INPUT
=========================
{document_text}

=========================
INSTRUCTIONS
=========================
1. Understand the legal context (case law, contract, statute, or opinion).  
2. Generate the summary using the selected **Output Format ({settings['output_format']})**:
   - **IRAC Format:** Issue, Rule, Application, Conclusion.
   - **Executive Summary:** Concise overview with key outcomes.
   - **Detailed Analysis:** In-depth reasoning and references.
   - **Bullet Points:** Structured and easy-to-scan summary.
3. Follow the selected **Citation Style ({settings['citation_style']})**.
4. Write in the specified **Language ({settings['language']})**.
5. Adjust detail level based on **Summary Length ({settings['summary_length']}%)**.
6. Include only the content types the user enabled as `true` in Content Inclusions.
7. Maintain a formal, professional legal tone and clear formatting.
8. Output should be ready for display or download in the frontend.

=========================
OUTPUT FORMAT
=========================
- Summary Title  
- Summary Body (according to {settings['output_format']})  
- Key Facts (if enabled)  
- Legal Issues (if enabled)  
- Holdings & Rulings (if enabled)  
- Recommendations (if enabled)  
- Confidence Score (based on {settings['confidence_threshold']}%)  
- Citation Style: {settings['citation_style']}  
- Language: {settings['language']}"""

        # Call GPT API
        from .services.gpt_client import call_gpt_api
        result = call_gpt_api("Legal Document Summarizer", prompt)
        summary_text = result['summary']
        
        # Save summary if auto_save enabled
        download_url = None
        filename = None
        file_size = 0
        document_id = None
        
        if settings['auto_save']:
            # Create document record and save summary
            if request.user.is_authenticated:
                user = request.user
            else:
                from accounts.models import User
                user, created = User.objects.get_or_create(
                    email='test@example.com',
                    defaults={'password': 'testpass123'}
                )
            
            uploaded_doc = UploadedDocument(
                user=user,
                file_name=f"summary_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                file_type='txt',
                file_size=len(summary_text.encode('utf-8'))
            )
            
            # Save summary as file
            from django.core.files.base import ContentFile
            uploaded_doc.file_path.save(
                uploaded_doc.file_name,
                ContentFile(summary_text.encode('utf-8'))
            )
            uploaded_doc.save()
            
            protocol = 'https' if request.is_secure() else 'http'
            download_url = f'{protocol}://{request.get_host()}{uploaded_doc.file_path.url}'
            filename = uploaded_doc.file_name
            file_size = uploaded_doc.file_size
            document_id = uploaded_doc.id
        
        return {
            'summary': summary_text,
            'word_count': len(summary_text.split()),
            'settings_used': settings,
            'truncated': False,
            'tokens_used': len(summary_text.split()) * 1.3,  # Estimate
            'model': 'gpt-3.5-turbo',
            'download_url': download_url,
            'filename': filename,
            'file_size': file_size,
            'document_id': document_id
        }
