"""
OCR Processor Module
Automatically processes PDF files and extracts text using OCR technology.
"""

import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from io import BytesIO
import json


class PDFOCRProcessor:
    """
    A class to handle OCR processing of PDF files.
    Automatically detects existing text and performs OCR on scanned content.
    """
    
    def __init__(self, tesseract_path=None):
        """
        Initialize the OCR processor.
        
        Args:
            tesseract_path (str): Path to tesseract executable if not in PATH
        """
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
    def process_pdf(self, pdf_path, output_format='text', language='eng'):
        """
        Process a PDF file and extract all text content.
        
        Args:
            pdf_path (str): Path to the PDF file
            output_format (str): Output format ('text', 'json', 'structured')
            language (str): Language code for OCR (default: 'eng')
            
        Returns:
            dict: Processing results with extracted text and metadata
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        results = {
            'file_path': pdf_path,
            'total_pages': 0,
            'pages_with_existing_text': 0,
            'pages_requiring_ocr': 0,
            'extracted_text': [],
            'processing_status': 'success',
            'errors': []
        }
        
        try:
            with fitz.open(pdf_path) as pdf_document:
                results['total_pages'] = pdf_document.page_count
                
                for page_num in range(pdf_document.page_count):
                    page_result = self._process_page(pdf_document, page_num, language)
                    results['extracted_text'].append(page_result)
                    
                    if page_result['has_existing_text']:
                        results['pages_with_existing_text'] += 1
                    else:
                        results['pages_requiring_ocr'] += 1
                        
        except Exception as e:
            results['processing_status'] = 'error'
            results['errors'].append(str(e))
        
        return self._format_output(results, output_format)
    
    def _process_page(self, pdf_document, page_num, language='eng'):
        """
        Process a single page of the PDF.
        
        Args:
            pdf_document: PyMuPDF document object
            page_num (int): Page number to process
            language (str): Language code for OCR
            
        Returns:
            dict: Page processing results
        """
        page = pdf_document[page_num]
        page_result = {
            'page_number': page_num + 1,
            'has_existing_text': False,
            'text': '',
            'ocr_performed': False,
            'confidence': None
        }
        
        try:
            # First, try to extract existing text
            existing_text = page.get_text().strip()
            
            if existing_text and len(existing_text) > 20:  # Substantial text exists
                page_result['text'] = existing_text
                page_result['has_existing_text'] = True
            else:
                # Perform OCR on the page
                ocr_result = self._perform_ocr_on_page(page, language)
                page_result['text'] = ocr_result['text']
                page_result['ocr_performed'] = True
                page_result['confidence'] = ocr_result['confidence']
                
        except Exception as e:
            page_result['error'] = str(e)
        
        return page_result
    
    def _perform_ocr_on_page(self, page, language='eng'):
        """
        Perform OCR on a single PDF page.
        
        Args:
            page: PyMuPDF page object
            language: Language code for OCR (default: 'eng')
            
        Returns:
            dict: OCR results with text and confidence
        """
        try:
            # Convert page to high-resolution image
            matrix = fitz.Matrix(2.0, 2.0)  # 2x zoom for better OCR
            pixmap = page.get_pixmap(matrix=matrix)
            image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
            
            # Perform OCR with confidence data
            ocr_data = pytesseract.image_to_data(
                image, 
                lang=language, 
                output_type=pytesseract.Output.DICT,
                config='--oem 3 --psm 6'
            )
            
            # Extract text and calculate average confidence
            words = []
            confidences = []
            
            for i, word in enumerate(ocr_data['text']):
                if word.strip():
                    words.append(word)
                    conf = ocr_data['conf'][i]
                    if conf > 0:
                        confidences.append(conf)
            
            text = ' '.join(words)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'text': text,
                'confidence': round(avg_confidence, 2)
            }
            
        except Exception as e:
            return {
                'text': '',
                'confidence': 0,
                'error': str(e)
            }
    
    def _format_output(self, results, output_format):
        """
        Format the output according to the specified format.
        
        Args:
            results (dict): Processing results
            output_format (str): Desired output format
            
        Returns:
            Various: Formatted output
        """
        if output_format == 'text':
            # Return plain text
            all_text = []
            for page in results['extracted_text']:
                if page['text'].strip():
                    all_text.append(f"--- Page {page['page_number']} ---\n{page['text']}")
            return '\n\n'.join(all_text)
        
        elif output_format == 'json':
            # Return JSON string
            return json.dumps(results, indent=2)
        
        elif output_format == 'structured':
            # Return structured data
            return results
        
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    def extract_text_only(self, pdf_path, language='eng'):
        """
        Quick method to extract only the text content.
        
        Args:
            pdf_path (str): Path to PDF file
            language (str): Language code for OCR
            
        Returns:
            str: Extracted text content
        """
        return self.process_pdf(pdf_path, output_format='text', language=language)
    
    def get_processing_summary(self, pdf_path):
        """
        Get a summary of the processing without full text extraction.
        
        Args:
            pdf_path (str): Path to PDF file
            
        Returns:
            dict: Processing summary
        """
        results = self.process_pdf(pdf_path, output_format='structured')
        
        return {
            'total_pages': results['total_pages'],
            'pages_with_existing_text': results['pages_with_existing_text'],
            'pages_requiring_ocr': results['pages_requiring_ocr'],
            'processing_status': results['processing_status'],
            'text_preview': results['extracted_text'][0]['text'][:200] + '...' if results['extracted_text'] else ''
        }


def process_pdf_file(pdf_path, output_format='text', language='eng'):
    """
    Convenience function to process a PDF file.
    
    Args:
        pdf_path (str): Path to PDF file
        output_format (str): Output format ('text', 'json', 'structured')
        language (str): Language code for OCR
        
    Returns:
        Various: Processing results
    """
    processor = PDFOCRProcessor()
    return processor.process_pdf(pdf_path, output_format, language)


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python ocr_processor.py <pdf_file_path> [output_format]")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    output_fmt = sys.argv[2] if len(sys.argv) > 2 else 'text'
    
    try:
        result = process_pdf_file(pdf_file, output_fmt)
        print(result)
    except Exception as e:
        print(f"Error processing PDF: {e}")