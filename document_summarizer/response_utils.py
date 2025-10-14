"""
Response utilities - handles PDF generation and download links
Input: summary data dict
Output: download URL and file metadata
"""
import os
from io import BytesIO
from django.core.files.base import ContentFile
from django.contrib.sites.shortcuts import get_current_site
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from datetime import datetime

def create_summary_pdf(summary_data):
    """Generate PDF from summary data with metadata"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    story.append(Paragraph("Document Summary", styles['Title']))
    story.append(Spacer(1, 12))
    
    # Metadata
    metadata = f"""
    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    Model: {summary_data.get('model', 'N/A')}
    Tokens Used: {summary_data.get('tokens_used', 'N/A')}
    Word Count: {summary_data.get('word_count', 'N/A')}
    """
    story.append(Paragraph(metadata, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Summary content
    story.append(Paragraph("Summary", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    summary_text = summary_data['summary'].replace('\n', '<br/>')
    story.append(Paragraph(summary_text, styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def create_download_link(summary_data, request):
    """Create downloadable PDF and return metadata"""
    pdf_content = create_summary_pdf(summary_data)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'summary_{timestamp}.pdf'
    
    # Get user
    if request.user.is_authenticated:
        user = request.user
    else:
        from accounts.models import User
        user, created = User.objects.get_or_create(
            email='test@example.com',
            defaults={'password': 'testpass123'}
        )
    
    # Save file
    from .models import UploadedDocument
    summary_doc = UploadedDocument(
        user=user,
        file_name=filename,
        file_type='pdf',
        file_size=len(pdf_content)
    )
    summary_doc.file_path.save(filename, ContentFile(pdf_content))
    summary_doc.save()
    
    # Generate URL
    current_site = get_current_site(request)
    base_url = f'http://{current_site.domain}'
    download_url = f'{base_url}{summary_doc.file_path.url}'
    
    return {
        'download_url': download_url,
        'filename': filename,
        'file_size': len(pdf_content),
        'document_id': summary_doc.id
    }