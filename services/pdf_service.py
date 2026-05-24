from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

def generate_pdf_from_text(text, title="Legal Notice"):
    """
    Generate a PDF from raw text, preserving basic formatting, bullets,
    and paragraphs, and return a BytesIO stream.
    """
    buffer = BytesIO()
    
    # Margins in points (72 points = 1 inch, 54 points = 0.75 inch)
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Define clean, professional legal document styles
    title_style = ParagraphStyle(
        'NoticeTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        alignment=TA_CENTER,
        spaceAfter=15
    )
    
    body_style = ParagraphStyle(
        'NoticeBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        alignment=TA_JUSTIFY,
        spaceAfter=8
    )
    
    story = []
    
    # Add Title
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 10))
    
    # Process text lines to maintain paragraphs and format lists
    lines = text.split('\n')
    for line in lines:
        stripped = line.strip()
        if not stripped:
            story.append(Spacer(1, 6))
            continue
        
        # Format list elements
        if stripped.startswith('- ') or stripped.startswith('* '):
            bullet_content = stripped[2:]
            bullet_style = ParagraphStyle(
                'NoticeBullet',
                parent=body_style,
                leftIndent=20,
                firstLineIndent=-10
            )
            story.append(Paragraph(f"&bull; {bullet_content}", bullet_style))
        elif stripped.startswith('1. ') or stripped.startswith('2. ') or stripped.startswith('3. ') or \
             stripped.startswith('4. ') or stripped.startswith('5. ') or stripped.startswith('6. '):
            # Numbered list item
            num_style = ParagraphStyle(
                'NoticeNumList',
                parent=body_style,
                leftIndent=20,
                firstLineIndent=-10
            )
            story.append(Paragraph(stripped, num_style))
        else:
            # Normal paragraph text
            story.append(Paragraph(stripped, body_style))
            
    doc.build(story)
    buffer.seek(0)
    return buffer
