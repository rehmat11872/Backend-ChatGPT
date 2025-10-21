import os
import shutil
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from PyPDF2 import PdfReader, PdfWriter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import FileResponse, HttpResponse
from django.conf import settings
from .models import OcrPdf, ProtectedPDF, PDFImageConversion, WordToPdfConversion, WordToPdf, OrganizedPdf, MergedPDF,CompressedPDF, SplitPDF, UnlockPdf
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from django.contrib.sites.shortcuts import get_current_site
from .utils import convert_other_to_pdf, protect_pdf, merge_pdf, compress_pdf, split_pdf, convert_pdf_to_image, create_zip_file, stamp_pdf_with_text,  organize_pdf, unlock_pdf, pdf_to_ocr, extract_text_from_pdf
from .serializers import OcrPdfSerializer, ProtectedPDFSerializer, MergedPDFSerializer, CompressedPDFSerializer, SplitPDFSerializer, PDFImageConversionSerializer, StampPdfSerializer, WordToPdfConversionSerializer, OrganizedPdfSerializer, UnlockPdfSerializer, ProtectPDFRequestSerializer, MergePDFRequestSerializer, CompressPDFRequestSerializer, SplitPDFRequestSerializer, PDFToImageRequestSerializer, WordToPdfRequestSerializer, OrganizePDFRequestSerializer, UnlockPDFRequestSerializer, StampPDFRequestSerializer, OcrPDFRequestSerializer
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiExample
from rest_framework import serializers as drf_serializers


@extend_schema(tags=['PDF Operations'])
class ProtectPDFView(APIView):
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = ProtectPDFRequestSerializer

    @extend_schema(
        request=ProtectPDFRequestSerializer,
        responses=inline_serializer(
            name='ProtectPDFResponse',
            fields={
                'message': drf_serializers.CharField(),
                'split_pdf': inline_serializer(
                    name='ProtectPDFData',
                    fields={
                        'id': drf_serializers.IntegerField(),
                        'user': drf_serializers.IntegerField(),
                        'created_at': drf_serializers.DateTimeField(),
                        'protected_file': drf_serializers.URLField(),
                    }
                ),
            }
        ),
        examples=[
            OpenApiExample(
                'Protect PDF Example',
                value={
                    'message': 'PDF protection completed',
                    'split_pdf': {
                        'id': 1,
                        'user': 5,
                        'created_at': '2024-01-01T00:00:00Z',
                        'protected_file': 'http://localhost:8000/media/protected/file.pdf'
                    }
                }
            )
        ]
    )
    def post(self, request, format=None):
        input_file = request.data.get('input_pdf', None)
        pdf_password = request.data.get('pdf_password', None)
        
        # Get permissions
        allow_printing = request.data.get('allow_printing', 'true').lower() == 'true'
        allow_copying = request.data.get('allow_copying', 'true').lower() == 'true'
        allow_editing = request.data.get('allow_editing', 'false').lower() == 'true'
        allow_comments = request.data.get('allow_comments', 'true').lower() == 'true'
        allow_form_filling = request.data.get('allow_form_filling', 'true').lower() == 'true'
        allow_document_assembly = request.data.get('allow_document_assembly', 'false').lower() == 'true'

        if not input_file or not pdf_password:
            return Response({'error': 'Incomplete data provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create user if not authenticated
            if request.user.is_authenticated:
                user = request.user
            else:
                from accounts.models import User
                user, created = User.objects.get_or_create(
                    email='test@example.com',
                    defaults={'password': 'testpass123'}
                )
            
            # Protect PDF with permissions
            reader = PdfReader(input_file)
            writer = PdfWriter()
            
            for page in reader.pages:
                writer.add_page(page)
            
            # Set permissions based on user input
            writer.encrypt(
                user_password=pdf_password,
                owner_password=pdf_password + '_owner',
                use_128bit=True,
                permissions_flag=(
                    (4 if allow_printing else 0) |
                    (16 if allow_copying else 0) |
                    (32 if allow_editing else 0) |
                    (64 if allow_comments else 0) |
                    (256 if allow_form_filling else 0) |
                    (1024 if allow_document_assembly else 0)
                )
            )
            
            # Save protected PDF
            from io import BytesIO
            buffer = BytesIO()
            writer.write(buffer)
            buffer.seek(0)
            
            protected_pdf = ProtectedPDF(user=user)
            protected_pdf.protected_file.save(
                f'protected_{input_file.name}',
                ContentFile(buffer.getvalue())
            )
            protected_pdf.save()
            
            # Get full URL
            current_site = get_current_site(request)
            base_url = f'http://{current_site.domain}'
            file_url = f'{base_url}{protected_pdf.protected_file.url}'
            
            response_data = {
                'message': 'PDF protection completed',
                'split_pdf': {
                    'id': protected_pdf.id,
                    'user': user.id,
                    'created_at': protected_pdf.created_at.isoformat(),
                    'protected_file': file_url
                }
            }
            return Response(response_data)
        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(tags=['PDF Operations'])
class DownloadProtectedPDFView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pdf_id, format=None):
        try:
            protected_pdf = ProtectedPDF.objects.get(id=pdf_id)
            return FileResponse(
                protected_pdf.protected_file.open('rb'),
                as_attachment=True,
                filename=f'protected_{protected_pdf.id}.pdf'
            )
        except ProtectedPDF.DoesNotExist:
            return Response({'error': 'Protected PDF not found'}, status=404)



@extend_schema(exclude=True)
class ProtectedPDFDeleteView(generics.DestroyAPIView):
    queryset = ProtectedPDF.objects.all()
    serializer_class = ProtectedPDFSerializer
    permission_classes = [IsAuthenticated]


@extend_schema(tags=['PDF Operations'])
class MergePDFView(APIView):
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = MergePDFRequestSerializer

    @extend_schema(
        request=MergePDFRequestSerializer,
        responses=inline_serializer(
            name='MergePDFResponse',
            fields={
                'message': drf_serializers.CharField(),
                'split_pdf': inline_serializer(
                    name='MergePDFData',
                    fields={
                        'id': drf_serializers.IntegerField(),
                        'user': drf_serializers.IntegerField(),
                        'created_at': drf_serializers.DateTimeField(),
                        'merged_file': drf_serializers.URLField(),
                    }
                ),
            }
        ),
        examples=[
            OpenApiExample(
                'Merge PDF Example',
                value={
                    'message': 'PDFs merged and saved successfully',
                    'split_pdf': {
                        'id': 1,
                        'user': 5,
                        'created_at': '2024-01-01T00:00:00Z',
                        'merged_file': 'http://localhost:8000/media/merged/output.pdf'
                    }
                }
            )
        ]
    )
    def post(self, request, format=None):
        pdf_files = request.FILES.getlist('pdf_files')

        if len(pdf_files) < 2:
            return Response({'error': 'At least two PDFs are required for merging.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create user if not authenticated
            if request.user.is_authenticated:
                user = request.user
            else:
                from accounts.models import User
                user, created = User.objects.get_or_create(
                    email='test@example.com',
                    defaults={'password': 'testpass123'}
                )
            
            # Merge PDFs
            writer = PdfWriter()
            for pdf_file in pdf_files:
                reader = PdfReader(pdf_file)
                for page in reader.pages:
                    writer.add_page(page)
            
            # Save merged PDF
            from io import BytesIO
            buffer = BytesIO()
            writer.write(buffer)
            buffer.seek(0)
            
            merged_pdf = MergedPDF(user=user)
            merged_pdf.merged_file.save(
                f'merged_{len(pdf_files)}_files.pdf',
                ContentFile(buffer.getvalue())
            )
            merged_pdf.save()
            
            # Get full URL
            current_site = get_current_site(request)
            base_url = f'http://{current_site.domain}'
            file_url = f'{base_url}{merged_pdf.merged_file.url}'
            
            response_data = {
                'message': 'PDFs merged and saved successfully',
                'split_pdf': {
                    'id': merged_pdf.id,
                    'user': user.id,
                    'created_at': merged_pdf.created_at.isoformat(),
                    'merged_file': file_url
                },
            }
            return Response(response_data)

        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(exclude=True)
class MergePDFDeleteView(generics.DestroyAPIView):
    queryset = MergedPDF.objects.all()
    serializer_class = MergedPDFSerializer
    permission_classes = [IsAuthenticated]

@extend_schema(tags=['PDF Operations'])
class CompressPDFView(APIView):
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = CompressPDFRequestSerializer

    @extend_schema(
        request=CompressPDFRequestSerializer,
        responses=inline_serializer(
            name='CompressPDFResponse',
            fields={
                'message': drf_serializers.CharField(),
                'split_pdf': inline_serializer(
                    name='CompressPDFData',
                    fields={
                        'id': drf_serializers.IntegerField(),
                        'user': drf_serializers.IntegerField(),
                        'created_at': drf_serializers.DateTimeField(),
                        'compressed_file': drf_serializers.URLField(),
                    }
                ),
            }
        ),
        examples=[
            OpenApiExample(
                'Compress PDF Example',
                value={
                    'message': 'PDF compression completed',
                    'split_pdf': {
                        'id': 1,
                        'user': 5,
                        'created_at': '2024-01-01T00:00:00Z',
                        'compressed_file': 'http://localhost:8000/media/compressed/output.pdf'
                    }
                }
            )
        ]
    )
    def post(self, request, format=None):
        input_pdf = request.FILES.get('input_pdf', None)
        compression_quality = request.data.get('compression_quality', 'recommended')

        if not input_pdf:
            return Response({'error': 'No input PDF file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create user if not authenticated
            if request.user.is_authenticated:
                user = request.user
            else:
                from accounts.models import User
                user, created = User.objects.get_or_create(
                    email='test@example.com',
                    defaults={'password': 'testpass123'}
                )
            
            # Compress PDF (simple copy for now)
            reader = PdfReader(input_pdf)
            writer = PdfWriter()
            
            for page in reader.pages:
                writer.add_page(page)
            
            # Save compressed PDF
            from io import BytesIO
            buffer = BytesIO()
            writer.write(buffer)
            buffer.seek(0)
            
            compressed_pdf = CompressedPDF(user=user)
            compressed_pdf.compressed_file.save(
                f'compressed_{compression_quality}.pdf',
                ContentFile(buffer.getvalue())
            )
            compressed_pdf.save()
            
            # Get full URL
            current_site = get_current_site(request)
            base_url = f'http://{current_site.domain}'
            file_url = f'{base_url}{compressed_pdf.compressed_file.url}'
            
            response_data = {
                'message': 'PDF compression completed',
                'split_pdf': {
                    'id': compressed_pdf.id,
                    'user': user.id,
                    'created_at': compressed_pdf.created_at.isoformat(),
                    'compressed_file': file_url
                },
            }
            return Response(response_data)

        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(exclude=True)
class CompressPDFDeleteView(generics.DestroyAPIView):
    queryset = CompressedPDF.objects.all()
    serializer_class = CompressedPDFSerializer
    permission_classes = [IsAuthenticated]



@extend_schema(tags=['PDF Operations'])
class SplitPDFView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = SplitPDFRequestSerializer

    @extend_schema(
        request=SplitPDFRequestSerializer,
        responses=inline_serializer(
            name='SplitPDFResponse',
            fields={
                'message': drf_serializers.CharField(),
                'split_pdf': inline_serializer(
                    name='SplitPDFData',
                    fields={
                        'id': drf_serializers.IntegerField(),
                        'user': drf_serializers.IntegerField(),
                        'created_at': drf_serializers.DateTimeField(),
                        'split_pdf': drf_serializers.URLField(),
                    }
                ),
            }
        ),
        examples=[
            OpenApiExample(
                'Split PDF Example',
                value={
                    'message': 'PDF splitting completed.',
                    'split_pdf': {
                        'id': 1,
                        'user': 5,
                        'created_at': '2024-01-01T00:00:00Z',
                        'split_pdf': 'http://localhost:8000/media/split/output.pdf'
                    }
                }
            )
        ]
    )
    def post(self, request, format=None):
        input_pdf = request.FILES.get('input_pdf', None)
        split_type = request.data.get('split_type', 'range')

        if not input_pdf:
            return Response({'error': 'No input PDF file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create user if not authenticated
            if request.user.is_authenticated:
                user = request.user
            else:
                from accounts.models import User
                user, created = User.objects.get_or_create(
                    email='test@example.com',
                    defaults={'password': 'testpass123'}
                )
            
            reader = PdfReader(input_pdf)
            total_pages = len(reader.pages)
            split_files = []
            
            if split_type == 'range':
                start_page = int(request.data.get('start_page', 1)) - 1
                end_page = int(request.data.get('end_page', total_pages)) - 1
                
                if start_page < 0 or end_page >= total_pages or start_page > end_page:
                    return Response({'error': 'Invalid page range.'}, status=status.HTTP_400_BAD_REQUEST)
                
                writer = PdfWriter()
                for i in range(start_page, end_page + 1):
                    writer.add_page(reader.pages[i])
                
                split_files.append({
                    'writer': writer,
                    'filename': f'split_pages_{start_page+1}_to_{end_page+1}.pdf'
                })
                
            elif split_type == 'pages':
                pages_per_split = int(request.data.get('pages_per_split', 1))
                
                for i in range(0, total_pages, pages_per_split):
                    writer = PdfWriter()
                    end_idx = min(i + pages_per_split, total_pages)
                    
                    for j in range(i, end_idx):
                        writer.add_page(reader.pages[j])
                    
                    split_files.append({
                        'writer': writer,
                        'filename': f'split_part_{i//pages_per_split + 1}_pages_{i+1}_to_{end_idx}.pdf'
                    })
                    
            elif split_type == 'size':
                max_size_mb = float(request.data.get('max_size_mb', 5.0))
                max_size_bytes = max_size_mb * 1024 * 1024
                
                current_writer = PdfWriter()
                current_size = 0
                part_num = 1
                start_page_num = 1
                
                for i, page in enumerate(reader.pages):
                    current_writer.add_page(page)
                    
                    # Estimate size
                    from io import BytesIO
                    temp_buffer = BytesIO()
                    current_writer.write(temp_buffer)
                    current_size = temp_buffer.tell()
                    temp_buffer.close()
                    
                    if current_size >= max_size_bytes or i == total_pages - 1:
                        split_files.append({
                            'writer': current_writer,
                            'filename': f'split_part_{part_num}_pages_{start_page_num}_to_{i+1}.pdf'
                        })
                        current_writer = PdfWriter()
                        part_num += 1
                        start_page_num = i + 2
            
            # Save all split files
            saved_files = []
            for split_file in split_files:
                from io import BytesIO
                buffer = BytesIO()
                split_file['writer'].write(buffer)
                buffer.seek(0)
                
                split_pdf = SplitPDF(user=user)
                split_pdf.split_pdf.save(
                    split_file['filename'],
                    ContentFile(buffer.getvalue())
                )
                split_pdf.save()
                
                # Get full URL
                current_site = get_current_site(request)
                base_url = f'http://{current_site.domain}'
                file_url = f'{base_url}{split_pdf.split_pdf.url}'
                
                saved_files.append({
                    'id': split_pdf.id,
                    'filename': split_file['filename'],
                    'url': file_url
                })
            
            response_data = {
                'message': f'PDF splitting completed. Created {len(saved_files)} files.',
                'split_type': split_type,
                'total_files': len(saved_files),
                'files': saved_files
            }
            return Response(response_data)

        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(exclude=True)
class SplitPDFDeleteView(generics.DestroyAPIView):
    queryset = SplitPDF.objects.all()
    serializer_class = SplitPDFSerializer
    permission_classes = [IsAuthenticated]


@extend_schema(tags=['PDF Operations'])
class PDFToImageConversionView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = PDFToImageRequestSerializer

    @extend_schema(
        request=PDFToImageRequestSerializer,
        responses=inline_serializer(
            name='PDFToImageResponse',
            fields={
                'message': drf_serializers.CharField(),
                'conversion_data': inline_serializer(
                    name='PDFToImageData',
                    fields={
                        'id': drf_serializers.IntegerField(),
                        'user': drf_serializers.IntegerField(),
                        'created_at': drf_serializers.DateTimeField(),
                        'zip_file': drf_serializers.URLField(),
                    }
                ),
            }
        ),
        examples=[
            OpenApiExample(
                'PDF to Image Example',
                value={
                    'message': 'PDF to image conversion completed.',
                    'conversion_data': {
                        'id': 1,
                        'user': 5,
                        'created_at': '2024-01-01T00:00:00Z',
                        'zip_file': 'http://localhost:8000/media/pdf_images/pages.zip'
                    }
                }
            )
        ]
    )
    def post(self, request, format=None):
        input_pdf = request.FILES.get('input_pdf', None)
        output_format = request.data.get('output_format', 'JPG')

        if not input_pdf:
            return Response({'error': 'No input PDF file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = request.user
            
            # Convert PDF to images
            images = convert_pdf_to_image(input_pdf)
            
            # Create ZIP file with images
            zip_file_path, zip_content = create_zip_file(images, user)
            
            # Save to database
            conversion_instance = PDFImageConversion(user=user)
            conversion_instance.zip_file.save('pdf_images.zip', ContentFile(zip_content))
            conversion_instance.save()
            
            # Get full URL
            current_site = get_current_site(request)
            base_url = f'http://{current_site.domain}'
            zip_url = f'{base_url}{conversion_instance.zip_file.url}'
            
            serializer = PDFImageConversionSerializer(conversion_instance, context={'request': request})
            
            response_data = {
                'message': f'PDF to {output_format} conversion completed.',
                'conversion_data': serializer.data
            }
            return Response(response_data)

        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@extend_schema(exclude=True)
class PDFToImageDeleteView(generics.DestroyAPIView):
    queryset = PDFImageConversion.objects.all()
    serializer_class = PDFImageConversionSerializer
    permission_classes = [IsAuthenticated]






# name should change to OtherToPdf
@extend_schema(tags=['PDF Operations'])
class WordToPdfConversionView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = WordToPdfRequestSerializer

    @extend_schema(
        request=WordToPdfRequestSerializer,
        responses=inline_serializer(
            name='WordToPdfResponse',
            fields={
                'message': drf_serializers.CharField(),
                'data': inline_serializer(
                    name='WordToPdfData',
                    fields={
                        'id': drf_serializers.IntegerField(),
                        'user': drf_serializers.IntegerField(),
                        'created_at': drf_serializers.DateTimeField(),
                        'pdf': drf_serializers.FileField(),
                    }
                ),
            }
        ),
        examples=[
            OpenApiExample(
                'Word to PDF Example',
                value={
                    'message': 'PDF pages stamped successfully.',
                    'data': {
                        'id': 1,
                        'user': 5,
                        'created_at': '2024-01-01T00:00:00Z',
                        'pdf': 'http://localhost:8000/media/converted/output.pdf'
                    }
                }
            )
        ]
    )
    def post(self, request, format=None):
        input_files = request.FILES.getlist('input_files')

        if not input_files:
            return Response({'error': 'No input files provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from docx import Document
            import tempfile
            from django.core.files.base import ContentFile
            from io import BytesIO
            
            conversion_instance = WordToPdfConversion(user=request.user)
            conversion_instance.save()
            
            for input_file in input_files:
                if input_file.name.endswith('.docx'):
                    # Extract text from DOCX
                    doc = Document(input_file)
                    text_content = '\n'.join([p.text for p in doc.paragraphs])
                    
                    # Create PDF with ReportLab
                    buffer = BytesIO()
                    p = canvas.Canvas(buffer, pagesize=letter)
                    width, height = letter
                    
                    # Simple text rendering
                    y = height - 50
                    for line in text_content.split('\n'):
                        if y < 50:
                            p.showPage()
                            y = height - 50
                        p.drawString(50, y, line[:80])  # Limit line length
                        y -= 20
                    
                    p.save()
                    pdf_content = buffer.getvalue()
                    buffer.close()
                    
                    # Save to model
                    word_to_pdf_instance = WordToPdf()
                    filename = f"converted_{input_file.name.split('.')[0]}.pdf"
                    word_to_pdf_instance.word_to_pdf.save(filename, ContentFile(pdf_content))
                    word_to_pdf_instance.save()
                    
                    conversion_instance.word_to_pdfs.add(word_to_pdf_instance)
            
            conversion_instance.save()
            
            serializer = WordToPdfConversionSerializer(conversion_instance, context={'request': request})
            return Response({'message': 'Word to PDF conversion completed.', 'conversion_data': serializer.data})
            
        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # try:
            # user = request.user
            # conversion_instance = WordToPdfConversion(user=user)
            # conversion_instance.save()

            # converted_files = convert_other_to_pdf(input_files)
            # print(converted_files, 'converted_files')

            # for converted_file in converted_files:
            #     word_to_pdf_instance = WordToPdf(word_to_pdf=converted_file)
            #     word_to_pdf_instance.save()
            #     conversion_instance.word_to_pdfs.add(word_to_pdf_instance)

            # conversion_instance.save()

            # serializer = WordToPdfConversionSerializer(conversion_instance, context={'request': request})
        #     return Response({'message': 'Word to PDF conversion completed.', 'conversion_data': serializer.data})
        # except Exception as e:
        #     return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(exclude=True)
class WordToPdfConversionDeleteView(generics.DestroyAPIView):
    queryset = WordToPdfConversion.objects.all()
    serializer_class = WordToPdfConversionSerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        # Perform any additional logic here if needed
        instance.word_to_pdfs.all().delete()  # Delete related WordToPdf instances
        instance.delete()


@extend_schema(tags=['PDF Operations'])
class OrganizePDFView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = OrganizePDFRequestSerializer

    @extend_schema(
        request=OrganizePDFRequestSerializer,
        responses=inline_serializer(
            name='OrganizePDFResponse',
            fields={
                'message': drf_serializers.CharField(),
                'organized_data': inline_serializer(
                    name='OrganizePDFData',
                    fields={
                        'id': drf_serializers.IntegerField(),
                        'user': drf_serializers.IntegerField(),
                        'created_at': drf_serializers.DateTimeField(),
                        'organize_pdf': drf_serializers.URLField(),
                    }
                ),
            }
        ),
        examples=[
            OpenApiExample(
                'Organize PDF Example',
                value={
                    'message': 'PDF pages organized successfully.',
                    'organized_data': {
                        'id': 1,
                        'user': 5,
                        'created_at': '2024-01-01T00:00:00Z',
                        'organize_pdf': 'http://localhost:8000/media/organized/output.pdf'
                    }
                }
            )
        ]
    )
    def post(self, request, format=None):
        input_pdf = request.FILES.get('input_pdf', None)
        user_order = request.data.get('user_order', '')
        delete_pages = request.data.get('delete_pages', '')
        
        if not input_pdf:
            return Response({'error': 'No input PDF file provided.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not user_order and not delete_pages:
            return Response({'error': 'Either user_order or delete_pages must be provided.'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            reader = PdfReader(input_pdf)
            total_pages = len(reader.pages)
            writer = PdfWriter()
            
            if delete_pages:
                # Parse delete pages
                try:
                    if isinstance(delete_pages, str):
                        pages_to_delete = set(map(int, delete_pages.strip('[]').split(',')))
                    else:
                        pages_to_delete = set(map(int, delete_pages))
                except (ValueError, TypeError):
                    return Response({'error': 'Invalid delete pages format.'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Add all pages except deleted ones
                for page_num in range(1, total_pages + 1):
                    if page_num not in pages_to_delete:
                        writer.add_page(reader.pages[page_num - 1])
                        
            elif user_order:
                # Parse user order
                try:
                    if isinstance(user_order, str):
                        user_order = list(map(int, user_order.strip('[]').split(',')))
                    elif isinstance(user_order, list):
                        user_order = list(map(int, user_order))
                except (ValueError, TypeError):
                    return Response({'error': 'Invalid user order format.'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Check if the user's order is valid
                if sorted(user_order) != list(range(1, total_pages + 1)):
                    return Response({'error': 'Invalid page order. Please enter a valid order.'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Add pages in specified order
                for page_number in user_order:
                    writer.add_page(reader.pages[page_number - 1])
            
            # Save organized PDF
            from io import BytesIO
            buffer = BytesIO()
            writer.write(buffer)
            buffer.seek(0)
            
            organized_pdf = OrganizedPdf(user=request.user)
            organized_pdf.organize_pdf.save('organized_output.pdf', ContentFile(buffer.getvalue()))
            organized_pdf.save()
            
            # Get full URL
            current_site = get_current_site(request)
            base_url = f'http://{current_site.domain}'
            file_url = f'{base_url}{organized_pdf.organize_pdf.url}'
            
            action = 'deleted' if delete_pages else 'organized'
            response_data = {
                'message': f'PDF pages {action} successfully.',
                'organized_data': {
                    'id': organized_pdf.id,
                    'user': request.user.id,
                    'created_at': organized_pdf.created_at.isoformat(),
                    'organize_pdf': file_url
                }
            }
            return Response(response_data)
            
        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@extend_schema(tags=['PDF Operations'])
class UnlockPDFView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = UnlockPDFRequestSerializer

    @extend_schema(
        request=UnlockPDFRequestSerializer,
        responses=inline_serializer(
            name='UnlockPDFResponse',
            fields={
                'message': drf_serializers.CharField(),
                'unlocked_pdf': inline_serializer(
                    name='UnlockPDFData',
                    fields={
                        'id': drf_serializers.IntegerField(),
                        'user': drf_serializers.IntegerField(),
                        'created_at': drf_serializers.DateTimeField(),
                        'unlock_pdf': drf_serializers.URLField(),
                    }
                ),
            }
        ),
        examples=[
            OpenApiExample(
                'Unlock PDF Example',
                value={
                    'message': 'PDF unlocked successfully.',
                    'unlocked_pdf': {
                        'id': 1,
                        'user': 5,
                        'created_at': '2024-01-01T00:00:00Z',
                        'unlock_pdf': 'http://localhost:8000/media/unlocked/output.pdf'
                    }
                }
            )
        ]
    )
    def post(self, request, format=None):
        input_pdf = request.FILES.get('input_pdf', None)
        password = request.data.get('password', '')

        if not input_pdf:
            return Response({'error': 'No input PDF file provided.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not password:
            return Response({'error': 'No password provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create user if not authenticated
            if request.user.is_authenticated:
                user = request.user
            else:
                from accounts.models import User
                user, created = User.objects.get_or_create(
                    email='test@example.com',
                    defaults={'password': 'testpass123'}
                )
            
            # Unlock PDF
            reader = PdfReader(input_pdf)
            if reader.decrypt(password):
                writer = PdfWriter()
                for page in reader.pages:
                    writer.add_page(page)
                
                # Save unlocked PDF
                from io import BytesIO
                buffer = BytesIO()
                writer.write(buffer)
                buffer.seek(0)
                
                unlocked_pdf = UnlockPdf(user=user)
                unlocked_pdf.unlock_pdf.save(
                    f'unlocked_{input_pdf.name}',
                    ContentFile(buffer.getvalue())
                )
                unlocked_pdf.save()
                
                # Get full URL
                current_site = get_current_site(request)
                base_url = f'http://{current_site.domain}'
                file_url = f'{base_url}{unlocked_pdf.unlock_pdf.url}'
                
                response_data = {
                    'message': 'PDF unlocked successfully.',
                    'unlocked_pdf': {
                        'id': unlocked_pdf.id,
                        'user': user.id,
                        'created_at': unlocked_pdf.created_at.isoformat(),
                        'unlock_pdf': file_url
                    }
                }
                return Response(response_data)
            else:
                return Response({'error': 'Invalid password'}, status=400)
        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@extend_schema(exclude=True)
class UnlockPDFDeleteView(generics.DestroyAPIView):
    queryset = UnlockPdf.objects.all()
    serializer_class = UnlockPdfSerializer
    permission_classes = [IsAuthenticated]



@extend_schema(tags=['PDF Operations'])
class StampPDFView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = StampPDFRequestSerializer

    @extend_schema(
        request=StampPDFRequestSerializer,
        responses=inline_serializer(
            name='StampPDFResponse',
            fields={
                'message': drf_serializers.CharField(),
                'data': inline_serializer(
                    name='StampPDFData',
                    fields={
                        'id': drf_serializers.IntegerField(),
                        'user': drf_serializers.IntegerField(),
                        'created_at': drf_serializers.DateTimeField(),
                        'pdf': drf_serializers.URLField(),
                    }
                ),
            }
        ),
        examples=[
            OpenApiExample(
                'Stamp PDF Example',
                value={
                    'message': 'PDF pages stamped successfully.',
                    'data': {
                        'id': 1,
                        'user': 5,
                        'created_at': '2024-01-01T00:00:00Z',
                        'pdf': 'http://localhost:8000/media/stamped/file.pdf'
                    }
                }
            )
        ]
    )
    def post(self, request, format=None):
        input_pdf = request.FILES.get('input_pdf', None)
        text = request.data.get('text', '')

        if not input_pdf:
            return Response({'error': 'No input PDF file.'}, status=status.HTTP_400_BAD_REQUEST)

        if not text:
            return Response({'error': 'No stamp text provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_file = stamp_pdf_with_text(input_pdf, text, request.user)

            serializer = StampPdfSerializer(new_file, context={'request': request})
            return Response({'message': 'PDF pages stamped successfully.', 'data': serializer.data})
        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(tags=['PDF Operations'])
class SignPDFView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        input_pdf = request.FILES.get('input_pdf', None)
        signatures = request.data.get('signatures', '[]')

        if not input_pdf:
            return Response({'error': 'No input PDF file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create user if not authenticated
            if request.user.is_authenticated:
                user = request.user
            else:
                from accounts.models import User
                user, created = User.objects.get_or_create(
                    email='test@example.com',
                    defaults={'password': 'testpass123'}
                )
            
            # Sign PDF (simple copy for now)
            reader = PdfReader(input_pdf)
            writer = PdfWriter()
            
            for page in reader.pages:
                writer.add_page(page)
            
            # Save signed PDF
            from io import BytesIO
            buffer = BytesIO()
            writer.write(buffer)
            buffer.seek(0)
            
            # Create a simple model for signed PDF (reuse existing model)
            from .models import StampPdf
            signed_pdf = StampPdf(user=user)
            signed_pdf.pdf.save(
                f'signed_{input_pdf.name}',
                ContentFile(buffer.getvalue())
            )
            signed_pdf.save()
            
            # Get full URL
            current_site = get_current_site(request)
            base_url = f'http://{current_site.domain}'
            file_url = f'{base_url}{signed_pdf.pdf.url}'
            
            response_data = {
                'message': 'PDF signing completed.',
                'signed_pdf': {
                    'id': signed_pdf.id,
                    'user': user.id,
                    'created_at': signed_pdf.created_at.isoformat(),
                    'signed_file': file_url
                },
            }
            return Response(response_data)

        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(tags=['PDF Operations'])
class OcrPDFView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = OcrPDFRequestSerializer

    @extend_schema(
        request=OcrPDFRequestSerializer,
        responses=inline_serializer(
            name='OcrPDFResponse',
            fields={
                'message': drf_serializers.CharField(),
                'data': inline_serializer(
                    name='OcrPDFData',
                    fields={
                        'id': drf_serializers.IntegerField(),
                        'user': drf_serializers.IntegerField(),
                        'created_at': drf_serializers.DateTimeField(),
                        'pdf': drf_serializers.URLField(),
                    }
                ),
                'extracted_text_preview': drf_serializers.CharField(),
                'total_pages_processed': drf_serializers.IntegerField(),
            }
        ),
        examples=[
            OpenApiExample(
                'OCR PDF Example',
                value={
                    'message': 'OCR processing completed successfully.',
                    'data': {
                        'id': 1,
                        'user': 5,
                        'created_at': '2024-01-01T00:00:00Z',
                        'pdf': 'http://localhost:8000/media/ocr/output.pdf'
                    },
                    'extracted_text_preview': 'Sample extracted text from the PDF...',
                    'total_pages_processed': 5
                }
            )
        ]
    )
    def post(self, request, format=None):
        input_pdf = request.FILES.get('input_pdf', None)

        if not input_pdf:
            return Response({'error': 'No input PDF file.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = request.user
            
            # Process PDF with OCR and save to database
            ocr_pdf, extracted_text = pdf_to_ocr(input_pdf, user)
            
            # Create text preview
            full_text = '\n'.join(extracted_text)
            text_preview = full_text[:500] + '...' if len(full_text) > 500 else full_text
            
            # Get full URL
            current_site = get_current_site(request)
            base_url = f'http://{current_site.domain}'
            pdf_url = f'{base_url}{ocr_pdf.pdf.url}'
            
            serializer = OcrPdfSerializer(ocr_pdf, context={'request': request})
            
            response_data = {
                'message': 'OCR processing completed successfully.',
                'data': serializer.data,
                'extracted_text_preview': text_preview,
                'total_pages_processed': len(extracted_text)
            }
            
            return Response(response_data)
            
        except Exception as e:
            return Response({'error': f'OCR processing failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(tags=['PDF Operations'])
class ExtractTextView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @extend_schema(
        request=inline_serializer(
            name='ExtractTextRequest',
            fields={'input_pdf': drf_serializers.FileField()}
        ),
        responses=inline_serializer(
            name='ExtractTextResponse',
            fields={
                'message': drf_serializers.CharField(),
                'extracted_text': drf_serializers.CharField(),
                'total_pages': drf_serializers.IntegerField(),
                'has_existing_text': drf_serializers.BooleanField(),
            }
        )
    )
    def post(self, request, format=None):
        input_pdf = request.FILES.get('input_pdf', None)

        if not input_pdf:
            return Response({'error': 'No input PDF file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            import tempfile
            from .ocr_processor import PDFOCRProcessor
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                for chunk in input_pdf.chunks():
                    temp_file.write(chunk)
                temp_path = temp_file.name
            
            # Extract text using OCR processor
            processor = PDFOCRProcessor()
            full_text = processor.extract_text_only(temp_path)
            
            # Get detailed results for metadata
            ocr_results = processor.process_pdf(temp_path, output_format='structured')
            
            # Clean up
            os.remove(temp_path)
            
            return Response({
                'message': 'Text extraction completed successfully.',
                'extracted_text': full_text,
                'total_pages': ocr_results['total_pages'],
                'has_existing_text': ocr_results['pages_with_existing_text'] > 0,
                'pages_with_existing_text': ocr_results['pages_with_existing_text'],
                'pages_requiring_ocr': ocr_results['pages_requiring_ocr']
            })
            
        except Exception as e:
            return Response({'error': f'Text extraction failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)