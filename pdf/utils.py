import os
import fitz
from PIL import Image
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
from django.core.files.base import ContentFile
from zipfile import ZipFile
from django.contrib.sites.shortcuts import get_current_site  
from rest_framework.reverse import reverse
from .models import ProtectedPDF,MergedPDF, CompressedPDF, SplitPDF

from django.conf import settings

TEMP_PATH = settings.TEMP_PATH


def protect_pdf(request, input_file, password, user):
    pdf_reader = PdfReader(input_file)
    pdf_writer = PdfWriter()
    input_file_name = input_file.name
    

    for page_num in range(len(pdf_reader.pages)):
        pdf_writer.add_page(pdf_reader.pages[page_num])

    pdf_writer.encrypt(password)

    buffer = BytesIO()
    pdf_writer.write(buffer)

    protected_file = ProtectedPDF(user=user, password=password)
    protected_file.protected_file.save(input_file_name, ContentFile(buffer.getvalue()))
    protected_file.save()

    current_site = get_current_site(request)
    base_url = f'http://{current_site.domain}'
    full_url = f'{base_url}{protected_file.protected_file.url}'

    return protected_file, full_url


def merge_pdf(request, user, pdf_list):
    pdf_writer = PdfWriter()

    for pdf_file in pdf_list:
        pdf_reader = PdfReader(pdf_file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            pdf_writer.add_page(page)

    buffer = BytesIO()
    pdf_writer.write(buffer)

    merged_pdf = MergedPDF(user=user)
    merged_pdf.merged_file.save('merged_output.pdf', ContentFile(buffer.getvalue()))
    merged_pdf.save()

    current_site = get_current_site(request)
    base_url = f'http://{current_site.domain}'
    full_url = f'{base_url}{merged_pdf.merged_file.url}'

    return merged_pdf, full_url


def compress_pdf(request, user, input_pdf, compression_quality):
    try:
        # Save the uploaded PDF file to a temporary location
        
        # temp_file_path = os.path.join(temp_path, input_pdf.name)
        temp_file_path = os.path.join(TEMP_PATH, input_pdf.name)

        with open(temp_file_path, 'wb') as temp_file:
            for chunk in input_pdf.chunks():
                temp_file.write(chunk)

        # Create a PDF document object using PyMuPDF
        pdf_document = fitz.open(temp_file_path)
        pdf_writer = fitz.open()
        print(pdf_writer, 'pdf_writer')

        for page_number in range(pdf_document.page_count):
            page = pdf_document[page_number]

            # Convert the page to a Pixmap
            pixmap = page.get_pixmap()

            # Convert the Pixmap to a PIL Image
            pil_image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)

            # Compress the PIL Image
            quality = get_compression_quality(compression_quality)
            compressed_image_stream = BytesIO()
            pil_image.save(compressed_image_stream, format="JPEG", quality=quality)

            # Create a new PDF document with the compressed image
            compressed_pdf_page = pdf_writer.new_page(width=pixmap.width, height=pixmap.height)
            compressed_pdf_page.insert_image(compressed_pdf_page.rect, stream=compressed_image_stream.getvalue())

        # Save the compressed PDF
        buffer = BytesIO()
        # pdf_writer.write(buffer)
        pdf_writer.save(buffer)

        # Create a new CompressedPDF model instance
        compressed_pdf = CompressedPDF(user=user, compression_quality=compression_quality)
        compressed_pdf.compressed_file.save('compressed_output.pdf', ContentFile(buffer.getvalue()))
        compressed_pdf.save()

        # Clean up the temporary file
        os.remove(temp_file_path)

        current_site = get_current_site(request)
        base_url = f'http://{current_site.domain}'
        full_url = f'{base_url}{compressed_pdf.compressed_file.url}'

        

        return compressed_pdf, full_url

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


def get_compression_quality(choice):
    # Define compression quality based on user choice
    if choice == 'extreme':
        return 100   # Less quality, high compression
    elif choice == 'recommended':
        return 50   # Good quality, good compression
    elif choice == 'less':
        return 10   # High quality, less compression
    else:
        raise ValueError("Invalid compression choice")



# def split_pdf(request, input_pdf, start_page, end_page, user):
#     pdf_reader = PdfReader(input_pdf)
#     # pdf_writer = PdfWriter()


#     ranges = []
#     while True:
#         start_page = start_page
#         end_page = end_page
#         ranges.append((start_page, end_page))

#         # more_ranges = input("Do you want to add another range? (yes/no): ").lower()
#         # if more_ranges != 'yes':
#         #     break

#     for i, (start_page, end_page) in enumerate(ranges):
#         pdf_writer = pdf_reader()
#         for page_num in range(start_page, end_page + 1):
#             pdf_writer.addPage(pdf_reader.getPage(page_num))

#     # for page_num in range(start_page, end_page + 1):
#     #     pdf_writer.add_page(pdf_reader.pages[page_num])

#     buffer = BytesIO()
#     pdf_writer.write(buffer)

#     # Create a new SplitPDF instance and save it
#     split_pdf_instance = SplitPDF(start_page=start_page, end_page=end_page)
#     split_pdf_instance.split_pdf.save(f'split.pdf', ContentFile(buffer.getvalue()))
#     split_pdf_instance.save()

#     current_site = get_current_site(request)
#     base_url = f'http://{current_site.domain}'
#     full_url = f'{base_url}{split_pdf_instance.split_pdf.url}'

#     return split_pdf_instance, full_url


def split_pdf(request, input_pdf, start_page, end_page, user):
    pdf_reader = PdfReader(input_pdf)
    ranges = [(start_page, end_page)]

    for i, (start, end) in enumerate(ranges):
        pdf_writer = PdfWriter()

        for page_num in range(start, end + 1):
            pdf_writer.add_page(pdf_reader.pages[page_num])

        buffer = BytesIO()
        pdf_writer.write(buffer)

        # Create a new SplitPDF instance and save it
        split_pdf_instance = SplitPDF(start_page=start, end_page=end, user=user)
        split_pdf_instance.split_pdf.save('split.pdf', ContentFile(buffer.getvalue()))
        split_pdf_instance.save()

    current_site = get_current_site(request)
    base_url = f'http://{current_site.domain}'
    full_url = f'{base_url}{split_pdf_instance.split_pdf.url}'  # Adjust as needed

    return split_pdf_instance, full_url


#convert pdf to images

def convert_pdf_to_image(input_pdf):
    temp_file_path = os.path.join(TEMP_PATH, input_pdf.name)
    with open(temp_file_path, 'wb') as temp_file:
        for chunk in input_pdf.chunks():
            temp_file.write(chunk)

    with fitz.open(temp_file_path) as pdf_document:  # Use a context manager to ensure proper closing
        image_paths = []
        for page_number in range(pdf_document.page_count):
            page = pdf_document[page_number]
            image = page.get_pixmap()
            image_data = image.tobytes()  # Extract raw image bytes
            image_paths.append(image_data)  # Append raw bytes directly

    os.remove(temp_file_path)  # Clean up the temporary file
    return image_paths


def create_zip_file(images, user):
    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, 'w') as zip_file:
        for i, image_data in enumerate(images):
            zip_file.writestr(f'page_{i + 1}.jpeg', image_data)
    
    # Ensure the directory exists before saving the zip file
    zip_dir = os.path.join('pdf_images/zips/', str(user.id))
    os.makedirs(zip_dir, exist_ok=True)

    zip_name = f'pdf_images.zip'  # Simplified zip file name
    zip_file_path = os.path.join(zip_dir, zip_name)
    with open(zip_file_path, 'wb') as zip_file:
        zip_file.write(zip_buffer.getvalue())
    
    return zip_file_path, zip_buffer.getvalue()




