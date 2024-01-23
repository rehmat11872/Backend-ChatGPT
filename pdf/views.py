from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from PyPDF2 import PdfReader, PdfWriter
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import FileResponse
from .models import ProtectedPDF
from django.shortcuts import get_object_or_404
from .utils import protect_pdf, merge_pdf, compress_pdf, split_pdf
from .serializers import ProtectedPDFSerializer, MergedPDFSerializer, CompressedPDFSerializer, SplitPDFSerializer


class ProtectPDFView(APIView):
    permission_classes = [IsAuthenticated]

    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        input_file = request.data.get('input_pdf', None)
        pdf_password = request.data.get('pdf_password', None)

        if not input_file or not pdf_password:
            return Response({'error': 'Incomplete data provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            protected_file, full_url = protect_pdf(request, input_file, pdf_password, request.user)
            serializer = ProtectedPDFSerializer(protected_file)
            return Response({'message': 'PDF protection completed.', 'protected_pdf': serializer.data, 'full_url': full_url})
        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DownloadProtectedPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pdf_id, format=None):
        protected_pdf = get_object_or_404(ProtectedPDF, id=pdf_id, user=request.user)
        file_path = protected_pdf.protected_file.path
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{protected_pdf.protected_file.name}"'
        return response


class MergePDFView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        pdf_files = request.FILES.getlist('pdf_files')

        if len(pdf_files) < 2:
            return Response({'error': 'At least two PDFs are required for merging.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = request.user if request.user.is_authenticated else None
            merged_pdf, full_url = merge_pdf(request, user, pdf_files)
            serializer = MergedPDFSerializer(merged_pdf)
            return Response({'message': 'PDFs merged and saved successfully.', 'merged_pdf': serializer.data, 'full_url': full_url})
        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class CompressPDFView(APIView):
    parser_classes = (MultiPartParser, FormParser)

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
                return Response({'message': 'PDF compression completed.', 'compressed_pdf': serializer.data, 'full_url': full_url})
            except Exception as e:
                return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SplitPDFView(APIView):
    def post(self, request, format=None):
        input_pdf = request.FILES.get('input_pdf', None)
        start_page = int(request.data.get('start_page', 0))
        end_page = int(request.data.get('end_page', 0))

        if not input_pdf:
            return Response({'error': 'No input PDF file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = request.user 
            split_pdf_instance, full_url= split_pdf(request, input_pdf, start_page, end_page, user)
            serializer = SplitPDFSerializer(split_pdf_instance)
            return Response({'message': 'PDF splitting completed.', 'split_pdf': serializer.data, 'full_url': full_url})
        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
