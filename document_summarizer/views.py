import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, OpenApiExample
from django.core.files.base import ContentFile
from .models import UploadedDocument
from .serializers import DocumentUploadSerializer, UploadedDocumentSerializer, TextExtractionSerializer, SummarizeRequestSerializer, SummaryResponseSerializer
from .text_extractor import extract_text
from .pipeline import generate_summary

@extend_schema(tags=['Document Summarizer'])
class DocumentUploadView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    
    @extend_schema(
        request=DocumentUploadSerializer,
        responses={201: UploadedDocumentSerializer},
        examples=[
            OpenApiExample(
                'Document Upload Success',
                value={
                    'message': 'Document uploaded successfully',
                    'document': {
                        'id': 1,
                        'file_name': 'sample.pdf',
                        'file_type': 'pdf',
                        'file_size': 1024000,
                        'created_at': '2024-01-01T00:00:00Z'
                    }
                }
            )
        ]
    )
    def post(self, request):
        serializer = DocumentUploadSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get or create test user for anonymous requests
            if request.user.is_authenticated:
                user = request.user
            else:
                from accounts.models import User
                user, created = User.objects.get_or_create(
                    email='test@example.com',
                    defaults={'password': 'testpass123'}
                )
            
            document_file = serializer.validated_data['document']
            
            # Get file info
            file_name = document_file.name
            file_extension = file_name.lower().split('.')[-1]
            file_size = document_file.size
            
            # Create document record
            uploaded_doc = UploadedDocument(
                user=user,
                file_name=file_name,
                file_type=file_extension,
                file_size=file_size
            )
            
            # Save file
            uploaded_doc.file_path.save(file_name, document_file)
            uploaded_doc.save()
            
            # Return response
            doc_serializer = UploadedDocumentSerializer(uploaded_doc)
            
            return Response({
                'message': 'Document uploaded successfully',
                'document': doc_serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': f'Upload failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(tags=['Document Summarizer'])
class DocumentRetrieveView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        responses={200: UploadedDocumentSerializer},
        examples=[
            OpenApiExample(
                'Document Retrieve Success',
                value={
                    'id': 1,
                    'file_name': 'sample.pdf',
                    'file_type': 'pdf',
                    'file_size': 1024000,
                    'created_at': '2024-01-01T00:00:00Z'
                }
            )
        ]
    )
    def get(self, request, document_id):
        try:
            document = UploadedDocument.objects.get(id=document_id)
            serializer = UploadedDocumentSerializer(document)
            return Response(serializer.data)
            
        except UploadedDocument.DoesNotExist:
            return Response({
                'error': 'Document not found'
            }, status=status.HTTP_404_NOT_FOUND)

@extend_schema(tags=['Document Summarizer'])
class DocumentTextExtractionView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        responses={200: TextExtractionSerializer},
        examples=[
            OpenApiExample(
                'Text Extraction Success',
                value={
                    'text': 'This is the extracted text from the document...',
                    'word_count': 150,
                    'truncated': False
                }
            )
        ]
    )
    def get(self, request, document_id):
        try:
            document = UploadedDocument.objects.get(id=document_id)
            
            # Extract text from document
            with document.file_path.open('rb') as file_obj:
                extracted_text = extract_text(file_obj, document.file_type)
            
            # Calculate word count and check if truncated
            word_count = len(extracted_text.split())
            truncated = extracted_text.endswith('...[truncated]')
            
            return Response({
                'text': extracted_text,
                'word_count': word_count,
                'truncated': truncated
            })
            
        except UploadedDocument.DoesNotExist:
            return Response({
                'error': 'Document not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'Text extraction failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(tags=['Document Summarizer'])
class DocumentSummarizeView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=SummarizeRequestSerializer,
        responses={200: SummaryResponseSerializer},
        examples=[
            OpenApiExample(
                'Summarize Request',
                value={
                    'text': 'This is a long legal document that needs to be summarized...',
                    'settings': {
                        'format': 'irac',
                        'summary_length': 30,
                        'confidence_threshold': 85,
                        'inclusions': ['facts', 'issues', 'holdings'],
                        'citation_style': 'bluebook',
                        'language': 'english'
                    }
                }
            ),
            OpenApiExample(
                'Summarize Response',
                value={
                    'summary': 'Issue: Contract dispute over payment terms\nRule: UCC governs sale of goods contracts\nAnalysis: Terms were clearly specified in writing\nConclusion: Plaintiff entitled to damages',
                    'word_count': 28,
                    'settings_used': {
                        'format': 'irac',
                        'summary_length': 30,
                        'confidence_threshold': 85
                    },
                    'truncated': False,
                    'tokens_used': 1250,
                    'model': 'gpt-3.5-turbo',
                    'download_url': 'http://localhost:8000/media/documents/summary_20241013_143022.pdf',
                    'filename': 'summary_20241013_143022.pdf',
                    'file_size': 15420,
                    'document_id': 5
                }
            )
        ]
    )
    def post(self, request):
        serializer = SummarizeRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            text = serializer.validated_data['text']
            settings_dict = serializer.validated_data.get('settings', {})
            
            # Run complete pipeline
            result = generate_summary(text, settings_dict, request)
            
            return Response(result)
            
        except Exception as e:
            return Response({
                'error': f'Summarization failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)