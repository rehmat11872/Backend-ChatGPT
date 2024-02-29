import os
import fitz
import PyPDF2
import tempfile
from PIL import Image
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import colors

import concurrent.futures
from docx2pdf import convert
from PyPDF2 import PdfReader, PdfWriter
from django.core.files.base import ContentFile
from zipfile import ZipFile
from django.contrib.sites.shortcuts import get_current_site
from rest_framework.reverse import reverse
from .models import ProtectedPDF,MergedPDF, CompressedPDF, SplitPDF, OrganizedPdf, StampPdf, UnlockPdf

import math

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
    base_url = f'https://{current_site.domain}'
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
    base_url = f'https://{current_site.domain}'
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
        try:
            os.remove(temp_file_path)
        except OSError as e:
            print(f"Error deleting temporary file: {e}")

        current_site = get_current_site(request)
        base_url = f'https://{current_site.domain}'
        full_url = f'{base_url}{compressed_pdf.compressed_file.url}'



        return compressed_pdf, full_url

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def stamp_pdf_with_text(input_pdf, stamp_text, user):
    try:
        temp_file_path = os.path.join(TEMP_PATH, input_pdf.name)
        output_file_path = os.path.join(TEMP_PATH, 'stamped_output.pdf')

        input_pdf_path = os.path.join(TEMP_PATH, input_pdf.name)
        pdf_reader = PdfReader(input_pdf_path)
        pdf_writer = PdfWriter()

        watermark_buffer = BytesIO()

        canvas = Canvas(watermark_buffer, pagesize=letter)
        canvas.setFillColor(colors.Color(0, 0, 0, alpha=0.2))
        canvas.setFont("Helvetica", 36)

        text_width = canvas.stringWidth(stamp_text, "Helvetica", 36)
        text_height = 36

        center_x = letter[0] / 2 - (text_width / 2)
        center_y = letter[1] / 2 - (text_height / 2)

        # Rotate the canvas and draw the rotated text
        # canvas.rotate(30)  # Rotate by 30 degrees clockwise
        canvas.drawString(center_x, center_y, stamp_text)
        canvas.save()

        for page_number in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_number]
            watermark_pdf = PdfReader(BytesIO(watermark_buffer.getvalue()))
            watermark_page = watermark_pdf.pages[0]
            page.merge_page(watermark_page)
            pdf_writer.add_page(page)

        output_buffer = BytesIO()
        pdf_writer.write(output_buffer)

        stamped_pdf_instance = StampPdf(user=user)
        stamped_pdf_instance.pdf.save('stamped_output.pdf', ContentFile(output_buffer.getvalue()))
        stamped_pdf_instance.save()

        return stamped_pdf_instance

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
# def stamp_pdf_with_text(input_pdf, stamp_text, user):
#     try:
#         temp_file_path = os.path.join(TEMP_PATH, input_pdf.name)

#         with open(temp_file_path, 'wb') as temp_file:
#             for chunk in input_pdf.chunks():
#                 temp_file.write(chunk)

#         pdf_document = fitz.open(temp_file_path)

#         for page_number in range(len(pdf_document)):
#             page = pdf_document[page_number]

#             rect = page.rect

#             font_size = 36
#             font_color = (0, 0, 0)  # Black color

#             # Calculate center coordinates for positioning the text
#             # text_width = page.get_text_width(stamp_text, fontsize=font_size)
#             # text_height = page.get_text_height(stamp_text, fontsize=font_size)
#             center_x = (rect.width - 50) / 2
#             center_y = (rect.height - 30) / 2

#             # Add the text stamp to the page
#             page.insert_text((center_x, center_y), stamp_text, fontsize=font_size, color=font_color)

#         # Create a BytesIO buffer and write the stamped PDF content
#         buffer = BytesIO()
#         pdf_document.save(buffer)
#         buffer.seek(0)

#         # Save the stamped PDF to the StampedPdf model
#         stamped_pdf_instance = StampPdf(user=user)
#         stamped_pdf_instance.pdf.save('stamped_output.pdf', ContentFile(buffer.getvalue()))
#         stamped_pdf_instance.save()

#         return stamped_pdf_instance

#     except Exception as e:
#         print(f"An error occurred: {str(e)}")
#         return None


# def stamp_pdf_with_text(input_pdf, stamp_text, user):
#     try:
#         # Open the input PDF file
#         print(input_pdf, 'input_pdf')
#         pdf_document = fitz.open(input_pdf)
#         print(pdf_document, 'pdf_document')

#         # Iterate through each page of the PDF
#         for page_number in range(len(pdf_document)):
#             page = pdf_document[page_number]

#             # Define the text properties
#             font_size = 12
#             font_color = (0, 0, 0)  # Black color

#             # Add the text stamp to the page
#             page.insert_text((100, 100), stamp_text, fontsize=font_size, color=font_color)

#         # Create a BytesIO buffer and write the stamped PDF content
#         buffer = BytesIO()
#         pdf_document.save(buffer)
#         buffer.seek(0)

#         # Save the stamped PDF to the StampedPdf model
#         stamped_pdf_instance = StampPdf(user=user)
#         stamped_pdf_instance.pdf.save('stamped_output.pdf', ContentFile(buffer.getvalue()))
#         stamped_pdf_instance.save()

#         print("PDF successfully stamped.")
#         return stamped_pdf_instance

#     except Exception as e:
#         print(f"An error occurred: {str(e)}")
#         return None


# def stamp_pdf_with_text(pdf_path, text, output_path):
#     try:
#         # Open the PDF document
#         pdf_document = fitz.open(pdf_path)

#         # Iterate through each page of the PDF
#         for page_number in range(len(pdf_document)):
#             page = pdf_document[page_number]

#             # Get the dimensions of the page
#             rect = page.rect

#             # Define the text properties
#             font_size = 12
#             font_color = (0, 0, 0)  # Black color
#             # font = page.get_font("helv")  # You can replace "helv" with any font name available in your system

#             # Add the text stamp to the page
#             page.insert_text((rect.width - 100, rect.height - 50), text, fontsize=font_size, color=font_color)

#         # Save the stamped PDF
#         pdf_document.save(output_path)
#         pdf_document.close()

#         return output_path

#     except Exception as e:
#         print(f"An error occurred while stamping the PDF: {str(e)}")
#         return None



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




def split_pdf(request, input_pdf, start_page, end_page, user):
    pdf_reader = PdfReader(input_pdf)
    print(f'Total number of pages: {len(pdf_reader.pages)}')
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
    base_url = f'https://{current_site.domain}'
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



#Word to pdf

# def perform_conversion(input_file, output_file):
#     if input_file.name.endswith(".docx"):
#         # Save the InMemoryUploadedFile to a temporary file
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_docx:
#             temp_docx.write(input_file.read())
#             temp_docx_path = temp_docx.name

#         try:
#             convert(temp_docx_path, output_file)
#             return output_file
#         except Exception as e:
#             print(f"Error during conversion: {e}")
#         finally:
#             # Remove the temporary file
#             os.remove(temp_docx_path)
#     else:
#         raise ValueError("Unsupported file format")



# def word_to_pdf(input_files):
#     converted_files = []

#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         futures = []

#         for input_file in input_files:
#             output_file = f"{input_file.name.split('.')[0]}_output.pdf"
#             futures.append(executor.submit(perform_conversion, input_file, output_file))

#         for future in concurrent.futures.as_completed(futures):
#             try:
#                 result = future.result()
#                 if result:
#                     converted_files.append(result)
#                     os.remove(result)
#             except Exception as e:
#                 print(f"Error: {e}")

#     return converted_files

import subprocess
import tempfile
import os

def convert_to_pdf(input_file_path, output_file_path):
    """
    Converts a Word document (.docx) to PDF using unoconv and LibreOffice.
    """
    try:
        # Use unoconv to convert the input Word document to PDF
        subprocess.run(['unoconv', '-f', 'pdf', '-o', output_file_path, input_file_path], check=True)
        return output_file_path
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")
        return None

def word_to_pdf(input_files):
    """
    Converts a list of Word files to PDF asynchronously.
    """
    converted_files = []

    with tempfile.TemporaryDirectory() as temp_dir:
        for input_file in input_files:
            try:
                if input_file.name.endswith(".docx"):
                    input_file_path = os.path.join(temp_dir, input_file.name)
                    output_file_path = os.path.join(temp_dir, f"{os.path.splitext(input_file.name)[0]}.pdf")

                    # Save the input Word file to temporary directory
                    with open(input_file_path, 'wb') as temp_file:
                        temp_file.write(input_file.read())

                    # Convert Word to PDF
                    converted_file_path = convert_to_pdf(input_file_path, output_file_path)

                    if converted_file_path:
                        converted_files.append(converted_file_path)
            except Exception as e:
                print(f"Error: {e}")

    return converted_files




def organize_pdf(input_pdf, user_order, user):
    with input_pdf.open(mode='rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        total_pages = len(pdf_reader.pages)

        # Check if the user's order is valid
        if sorted(user_order) != list(range(1, total_pages + 1)):
            raise ValueError("Invalid page order. Please enter a valid order.")

        pdf_writer = PyPDF2.PdfWriter()
        for page_number in user_order:
            pdf_writer.add_page(pdf_reader.pages[page_number - 1])  # Adjusting for 0-based indexing

        # Create a BytesIO buffer and write the PDF content
        buffer = BytesIO()
        pdf_writer.write(buffer)
        buffer.seek(0)

        # Save the organized PDF to the OrganizedPdf model
        organized_pdf_instance = OrganizedPdf(user=user)
        organized_pdf_instance.organize_pdf.save(f"organized_output.pdf", ContentFile(buffer.getvalue()))
        organized_pdf_instance.save()

        print("PDF successfully organized.")
        return organized_pdf_instance




def unlock_pdf(input_pdf, password, user):
    pdf_reader = PyPDF2.PdfReader(input_pdf)


    # Try to decrypt the PDF with the provided password
    success = pdf_reader.decrypt(password)

    if success:
        # Create a PDF writer object
        pdf_writer = PyPDF2.PdfWriter()

        # Add each page from the decrypted PDF to the writer
        for page_num in range(len(pdf_reader.pages)):
            pdf_writer.add_page(pdf_reader.pages[page_num])

        # Create a BytesIO buffer and write the PDF content
        buffer = BytesIO()
        pdf_writer.write(buffer)
        buffer.seek(0)

        # Save the unlocked PDF to the UnlockPdf model
        unlock_pdf_instance = UnlockPdf(user=user)
        unlock_pdf_instance.unlock_pdf.save(f"unlocked_output.pdf", ContentFile(buffer.getvalue()))
        unlock_pdf_instance.save()

        print("PDF unlocked successfully.")
        return unlock_pdf_instance
    else:
        raise ValueError("Failed to unlock the PDF. Incorrect password.")