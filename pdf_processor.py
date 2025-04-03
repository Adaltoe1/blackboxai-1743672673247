import os
import pdfplumber
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from io import BytesIO
from config import UPLOAD_FOLDER
from datetime import datetime

def generate_pdf(source, filename=None, source_type='text'):
    """Generate PDF from different source types"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"generated_{timestamp}.pdf"
    
    output_path = os.path.join(UPLOAD_FOLDER, filename)
    c = canvas.Canvas(output_path, pagesize=letter)
    
    if source_type == 'text':
        c.setFont("Helvetica", 12)
        text = c.beginText(40, 750)
        for line in source.split('\n'):
            text.textLine(line)
            if text.getY() < 40:  # Check if we need a new page
                c.drawText(text)
                c.showPage()
                text = c.beginText(40, 750)
        c.drawText(text)
    elif source_type == 'url':
        # Placeholder for URL to PDF conversion
        c.drawString(100, 750, f"PDF generated from URL: {source}")
    elif source_type == 'file':
        # Placeholder for file conversion
        c.drawString(100, 750, f"PDF generated from file: {source}")
    
    c.save()
    return output_path

def extract_data(pdf_path):
    """Extract text and metadata from PDF"""
    results = {
        'filename': os.path.basename(pdf_path),
        'pages': 0,
        'text': '',
        'metadata': {},
        'size': os.path.getsize(pdf_path)
    }
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            results['pages'] = len(pdf.pages)
            for page in pdf.pages:
                results['text'] += page.extract_text() + '\n'
            
            if pdf.metadata:
                results['metadata'] = {
                    'title': pdf.metadata.get('Title', ''),
                    'author': pdf.metadata.get('Author', ''),
                    'creator': pdf.metadata.get('Creator', ''),
                    'creation_date': pdf.metadata.get('CreationDate', '')
                }
    except Exception as e:
        print(f"Error processing PDF: {e}")
    
    return results

def process_uploaded_file(file):
    """Process uploaded file and convert to PDF if needed"""
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    if filename.lower().endswith('.pdf'):
        return filepath, extract_data(filepath)
    else:
        # Convert non-PDF files to PDF
        pdf_filename = f"{os.path.splitext(filename)[0]}.pdf"
        pdf_path = generate_pdf(filepath, pdf_filename, 'file')
        return pdf_path, extract_data(pdf_path)