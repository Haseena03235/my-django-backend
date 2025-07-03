from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from django.conf import settings
import os
from datetime import datetime

def generate_quotation_pdf(ticket, quotation):
    """
    Generate a PDF quotation for a ticket
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    story.append(Paragraph("SERVICE QUOTATION", title_style))
    story.append(Spacer(1, 20))
    
    # Company Information
    company_style = ParagraphStyle(
        'CompanyInfo',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_CENTER
    )
    story.append(Paragraph("KLEVANT TECHNOLOGIES", company_style))
    story.append(Paragraph("Your Trusted Service Partner", company_style))
    story.append(Paragraph("Phone: +91 9876543210 | Email: info@klevant.com", company_style))
    story.append(Spacer(1, 20))
    
    # Quotation Details
    story.append(Paragraph("Quotation Details", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    # Customer Information
    customer_data = [
        ['Customer Name:', ticket.customer_name],
        ['Mobile:', ticket.customer_mobile],
        ['Address:', ticket.address],
        ['Service Type:', ticket.get_service_type_display()],
        ['Ticket ID:', f"#{ticket.id}"],
        ['Date Raised:', ticket.date_raised.strftime('%d/%m/%Y %H:%M')],
        ['Quotation Date:', quotation.created_at.strftime('%d/%m/%Y %H:%M')],
    ]
    
    customer_table = Table(customer_data, colWidths=[2*inch, 4*inch])
    customer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(customer_table)
    story.append(Spacer(1, 20))
    
    # Service Description
    story.append(Paragraph("Service Description", styles['Heading2']))
    story.append(Spacer(1, 10))
    story.append(Paragraph(ticket.description, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Quotation Items
    story.append(Paragraph("Quotation Items", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    # Table headers
    item_data = [['S.No', 'Description', 'Quantity', 'Price (₹)', 'Total (₹)']]
    
    # Add items
    total_amount = 0
    for i, item in enumerate(quotation.items.all(), 1):
        item_total = float(item.price) * item.quantity
        total_amount += item_total
        item_data.append([
            str(i),
            item.description,
            str(item.quantity),
            f"₹{item.price}",
            f"₹{item_total:.2f}"
        ])
    
    # Add total row
    item_data.append(['', '', '', 'Total:', f"₹{total_amount:.2f}"])
    
    item_table = Table(item_data, colWidths=[0.5*inch, 3*inch, 1*inch, 1*inch, 1*inch])
    item_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, -1), (-2, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    story.append(item_table)
    story.append(Spacer(1, 20))
    
    # Terms and Conditions
    story.append(Paragraph("Terms and Conditions", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    terms = [
        "1. This quotation is valid for 7 days from the date of issue.",
        "2. Payment is due upon completion of service.",
        "3. Warranty is provided as per manufacturer guidelines.",
        "4. Additional charges may apply for parts replacement.",
        "5. Service will be scheduled based on technician availability.",
        "6. Cancellation requires 24 hours notice.",
    ]
    
    for term in terms:
        story.append(Paragraph(term, styles['Normal']))
    
    story.append(Spacer(1, 20))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.grey
    )
    story.append(Paragraph("Thank you for choosing KLEVANT TECHNOLOGIES", footer_style))
    story.append(Paragraph("For any queries, please contact us at info@klevant.com", footer_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def save_quotation_pdf(ticket, quotation):
    """
    Save quotation PDF to media directory
    """
    buffer = generate_quotation_pdf(ticket, quotation)
    
    # Create filename
    filename = f"quotation_ticket_{ticket.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(settings.MEDIA_ROOT, 'quotations', filename)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Save file
    with open(filepath, 'wb') as f:
        f.write(buffer.getvalue())
    
    return filepath 