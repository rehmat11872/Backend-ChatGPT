import os
import shutil
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from PyPDF2 import PdfReader, PdfWriter
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import FileResponse
from .models import ProtectedPDF, PDFImageConversion, WordToPdfConversion, WordToPdf, OrganizedPdf, MergedPDF,CompressedPDF, SplitPDF, UnlockPdf
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from django.contrib.sites.shortcuts import get_current_site
from .utils import convert_other_to_pdf, pdf_to_ocr, protect_pdf, merge_pdf, compress_pdf, split_pdf, convert_pdf_to_image, create_zip_file, stamp_pdf_with_text,  organize_pdf, unlock_pdf
from .serializers import OcrPdfSerializer, ProtectedPDFSerializer, MergedPDFSerializer, CompressedPDFSerializer, SplitPDFSerializer, PDFImageConversionSerializer, StampPdfSerializer, WordToPdfConversionSerializer, OrganizedPdfSerializer, UnlockPdfSerializer, ProtectPDFRequestSerializer, MergePDFRequestSerializer, CompressPDFRequestSerializer, SplitPDFRequestSerializer, PDFToImageRequestSerializer, WordToPdfRequestSerializer, OrganizePDFRequestSerializer, UnlockPDFRequestSerializer, StampPDFRequestSerializer, OcrPDFRequestSerializer
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiExample
from rest_framework import serializers as drf_serializers


@extend_schema(tags=['PDF Operations'])
class ProtectPDFView(APIView):
    permission_classes = [IsAuthenticated]
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

        if not input_file or not pdf_password:
            return Response({'error': 'Incomplete data provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            protected_file, full_url = protect_pdf(request, input_file, pdf_password, request.user)
            serializer = ProtectedPDFSerializer(protected_file)

            response_data = {
                'message': 'PDF protection completed',
                'split_pdf': {
                    'id': serializer.data['id'],
                    'user': serializer.data['user'],
                    'created_at': serializer.data['created_at'],
                    'protected_file': full_url,
                    },
                }
            return Response(response_data)
        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(tags=['PDF Operations'])
class DownloadProtectedPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pdf_id, format=None):
        protected_pdf = get_object_or_404(ProtectedPDF, id=pdf_id, user=request.user)
        file_path = protected_pdf.protected_file.path
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{protected_pdf.protected_file.name}"'
        return response



@extend_schema(exclude=True)
class ProtectedPDFDeleteView(generics.DestroyAPIView):
    queryset = ProtectedPDF.objects.all()
    serializer_class = ProtectedPDFSerializer
    permission_classes = [IsAuthenticated]


@extend_schema(tags=['PDF Operations'])
class MergePDFView(APIView):
    permission_classes = [IsAuthenticated]
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
            user = request.user if request.user.is_authenticated else None
            merged_pdf, full_url = merge_pdf(request, user, pdf_files)
            serializer = MergedPDFSerializer(merged_pdf)

            response_data = {
                'message': 'PDFs merged and saved successfully',
                'split_pdf': {
                    'id': serializer.data['id'],
                    'user': serializer.data['user'],
                    'created_at': serializer.data['created_at'],
                    'merged_file': full_url,
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
    permission_classes = [IsAuthenticated]
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
            print(input_pdf, 'input_pdf')
            compression_quality = request.data.get('compression_quality', 'recommended')
            print(compression_quality, 'compression_quality')

            if not input_pdf:
                return Response({'error': 'No input PDF file provided.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = request.user
                compressed_pdf, full_url = compress_pdf(request, user, input_pdf, compression_quality)
                serializer = CompressedPDFSerializer(compressed_pdf)



                response_data = {
                'message': 'PDF compression completed',
                "compressed_pdf": {
                    'id': serializer.data['id'],
                    'user': serializer.data['user'],
                    'created_at': serializer.data['created_at'],
                    'compressed_file': full_url,
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
        start_page = int(request.data.get('start_page', 0))- 1
        end_page = int(request.data.get('end_page', 0))- 1

        print(start_page, end_page, 'print')

        if not input_pdf:
            return Response({'error': 'No input PDF file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = request.user
            split_pdf_instance, full_url= split_pdf(request, input_pdf, start_page, end_page, user)
            serializer = SplitPDFSerializer(split_pdf_instance)

            response_data = {
                'message': 'PDF splitting completed.',
                'split_pdf': {
                    'id': serializer.data['id'],
                    'user': serializer.data['user'],
                    'created_at': serializer.data['created_at'],
                    'split_pdf': full_url,
                },
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

        if not input_pdf:
            return Response({'error': 'No input PDF file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = request.user
            # output_folder = 'pdf_images'
            image_paths = convert_pdf_to_image(input_pdf)

            if len(image_paths) == 1:
                print('working')
                # Only one image, save it directly
                pdf_image_conversion = PDFImageConversion(user=user)
                pdf_image_conversion.zip_file.save(f'page_1.jpeg', ContentFile(image_paths[0]))
                pdf_image_conversion.save()
            else:
                # Multiple images, create a zip file
                # zip_file_path = create_zip_file(image_paths, user)

                zip_file_relative_path, zip_content = create_zip_file(image_paths, user)
                pdf_image_conversion = PDFImageConversion(user=user)
                pdf_image_conversion.zip_file.save(zip_file_relative_path, ContentFile(zip_content))
                pdf_image_conversion.save()

                shutil.rmtree(os.path.dirname(zip_file_relative_path))


            # Construct the full URL
            current_site = get_current_site(request)
            base_url = f'http://{current_site.domain}'
            zip_file_full_url = f'{base_url}{pdf_image_conversion.zip_file.url}'

            serializer = PDFImageConversionSerializer(pdf_image_conversion)
            response_data = {
                'message': 'PDF to image conversion completed.',
                'conversion_data': {
                    'id': serializer.data['id'],
                    'user': serializer.data['user'],
                    'created_at': serializer.data['created_at'],
                    'zip_file': zip_file_full_url,
                },
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
        input_file = request.FILES.get('input_file')

        if not input_file:
            return Response({'error': 'No input files provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # new_file = convert_other_to_pdf(input_file, request.user)
            new_file = convert_other_to_pdf(input_file)
            print(new_file,'new_file')

            serializer = StampPdfSerializer(new_file, context={'request': request})
            return Response({'message': 'PDF pages stamped successfully.', 'data': serializer.data})
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
        try:
            # Convert the string to a list
            user_order = list(map(int, user_order.strip('[]').split(',')))
            print(type(user_order))
        except ValueError:
            return Response({'error': 'Invalid user order format.'}, status=status.HTTP_400_BAD_REQUEST)


        if not input_pdf or not user_order:
            return Response({'error': 'No input PDF file or user order provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = request.user
            user_order = list(map(int, user_order))
            converted_file = organize_pdf(input_pdf, user_order, user)

            serializer = OrganizedPdfSerializer(converted_file, context={'request': request})
            return Response({'message': 'PDF pages organized successfully.', 'organized_data': serializer.data})
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

        if not input_pdf or not password:
            return Response({'error': 'Incomplete data. Please provide input PDF,  and password.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = request.user
            unlock_file = unlock_pdf(input_pdf, password, user)
            serializer = UnlockPdfSerializer(unlock_file, context={'request': request})
            return Response({'message': 'PDF unlocked successfully.', 'unlocked_pdf': serializer.data})
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
            }
        ),
        examples=[
            OpenApiExample(
                'OCR PDF Example',
                value={
                    'message': 'OCR to PDF conversion successful.',
                    'data': {
                        'id': 1,
                        'user': 5,
                        'created_at': '2024-01-01T00:00:00Z',
                        'pdf': 'http://localhost:8000/media/ocr/output.pdf'
                    }
                }
            )
        ]
    )
    def post(self, request, format=None):
        input_pdf = request.FILES.get('input_pdf', None)

        if not input_pdf:
            return Response({'error': 'No input PDF file.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_file = pdf_to_ocr(input_pdf, request.user)
            print(new_file,'new_file')

            serializer = OcrPdfSerializer(new_file, context={'request': request})
            return Response({'message': 'OCR to PDF conversion successful.', 'data': serializer.data})
        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)