"""
Text extraction from documents
Input: file object and file type
Output: extracted text string
Dependencies: PyMuPDF, python-docx
"""
# import fitz  # PyMuPDF
import pymupdf as fitz
from docx import Document
from io import BytesIO

class TextExtractor:
    MAX_TEXT_LENGTH = 50000  # Safe length for processing
    
    @staticmethod
    def extract_text(file_obj, file_type):
        """Extract text from uploaded file based on type"""
        try:
            if file_type == 'pdf':
                return TextExtractor._extract_from_pdf(file_obj)
            elif file_type == 'docx':
                return TextExtractor._extract_from_docx(file_obj)
            elif file_type == 'txt':
                return TextExtractor._extract_from_txt(file_obj)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        except Exception as e:
            raise Exception(f"Text extraction failed: {str(e)}")
    
    @staticmethod
    def _extract_from_pdf(file_obj):
        """Extract text from PDF using PyMuPDF"""
        file_obj.seek(0)
        pdf_bytes = file_obj.read()
        
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            text = ""
            for page in doc:
                text += page.get_text()
        
        return TextExtractor._truncate_text(text)
    
    @staticmethod
    def _extract_from_docx(file_obj):
        """Extract text from DOCX using python-docx"""
        file_obj.seek(0)
        doc = Document(file_obj)
        
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        return TextExtractor._truncate_text(text)
    
    @staticmethod
    def _extract_from_txt(file_obj):
        """Extract text from TXT file"""
        file_obj.seek(0)
        text = file_obj.read().decode('utf-8')
        return TextExtractor._truncate_text(text)
    
    @staticmethod
    def _truncate_text(text):
        """Truncate text if it exceeds safe length"""
        text = text.strip()
        if len(text) > TextExtractor.MAX_TEXT_LENGTH:
            return text[:TextExtractor.MAX_TEXT_LENGTH] + "...[truncated]"
        return text
