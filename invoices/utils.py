from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from django.http import HttpResponse
from django.utils import timezone

def generate_invoice_pdf(invoice):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#1E3A8A'),
        alignment=TA_LEFT,
        spaceAfter=12
    )
    
    heading_style = ParagraphStyle(
        'HeadingStyle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=HexColor('#3B82F6'),
        alignment=TA_LEFT,
        spaceAfter=6
    )
    
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14
    )
    
    # Content
    content = []
    
    # Header with Mookh Logo
    header_text = f"""
    <font size="24" color="#1E3A8A"><b>MOOKH</b></font><br/>
    <font size="12" color="#3B82F6">Ticket Validation System</font><br/>
    <font size="10">123 Business Street, City, Country</font><br/>
    <font size="10">contact@mookh.com | www.mookh.com</font>
    """
    content.append(Paragraph(header_text, title_style))
    content.append(Spacer(1, 20))
    
    # Invoice Title
    invoice_title = f"<font size='18' color='#1E3A8A'><b>INVOICE #{invoice.id:06d}</b></font>"
    content.append(Paragraph(invoice_title, title_style))
    content.append(Spacer(1, 20))
    
    # Bill To and Invoice Details Table
    bill_to_data = [
        ['<b>Bill To:</b>', '<b>Invoice Details:</b>'],
        [invoice.event_assignment.team_member.user.get_full_name(), f'<b>Invoice Date:</b> {invoice.invoice_date}'],
        [invoice.event_assignment.team_member.user.email, f'<b>Due Date:</b> {invoice.due_date}'],
        [invoice.event_assignment.team_member.phone, f'<b>Status:</b> {invoice.get_status_display()}'],
        ['', f'<b>Payment Terms:</b> 30 days']
    ]
    
    bill_to_table = Table(bill_to_data, colWidths=[2.5*inch, 2.5*inch])
    bill_to_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TEXTCOLOR', (0, 0), (-1, -1), black),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    content.append(bill_to_table)
    content.append(Spacer(1, 20))
    
    # Event Details
    event_heading = Paragraph("<b>Event Details:</b>", heading_style)
    content.append(event_heading)
    
    event_data = [
        f"<b>Event:</b> {invoice.event_assignment.event.name}",
        f"<b>Location:</b> {invoice.event_assignment.event.location}",
        f"<b>Dates:</b> {invoice.event_assignment.event.start_date.strftime('%B %d, %Y')} to {invoice.event_assignment.event.end_date.strftime('%B %d, %Y')}",
        f"<b>Role:</b> {'Team Lead' if invoice.event_assignment.is_team_lead else 'Team Member'}"
    ]
    
    for item in event_data:
        content.append(Paragraph(item, normal_style))
    
    content.append(Spacer(1, 20))
    
    # Invoice Items Table
    items_heading = Paragraph("<b>Invoice Items:</b>", heading_style)
    content.append(items_heading)
    
    items_data = [
        ['<b>Description</b>', '<b>Hours</b>', '<b>Rate</b>', '<b>Amount</b>'],
        ['Event Ticket Validation Services', 
         f"{invoice.total_hours}", 
         f"${invoice.hourly_rate:.2f}", 
         f"${invoice.total_amount:.2f}"]
    ]
    
    items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1*inch, 1*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 1, black),
    ]))
    content.append(items_table)
    content.append(Spacer(1, 20))
    
    # Total Amount
    total_data = [
        ['', '', '<b>Subtotal:</b>', f"${invoice.total_amount:.2f}"],
        ['', '', '<b>Tax (0%):</b>', '$0.00'],
        ['', '', '<b>Total:</b>', f"<font size='12'><b>${invoice.total_amount:.2f}</b></font>"]
    ]
    
    total_table = Table(total_data, colWidths=[3*inch, 1*inch, 1*inch, 1*inch])
    total_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    content.append(total_table)
    content.append(Spacer(1, 30))
    
    # Bank Details
    bank_heading = Paragraph("<b>Bank Details:</b>", heading_style)
    content.append(bank_heading)
    
    bank_data = [
        f"<b>Bank Name:</b> {invoice.event_assignment.team_member.bank_name}",
        f"<b>Account Number:</b> {invoice.event_assignment.team_member.account_number}",
        f"<b>IFSC Code:</b> {invoice.event_assignment.team_member.ifsc_code}"
    ]
    
    for item in bank_data:
        content.append(Paragraph(item, normal_style))
    
    content.append(Spacer(1, 20))
    
    # Additional Notes
    if invoice.additional_notes:
        notes_heading = Paragraph("<b>Additional Notes:</b>", heading_style)
        content.append(notes_heading)
        content.append(Paragraph(invoice.additional_notes, normal_style))
        content.append(Spacer(1, 20))
    
    # Footer
    footer_text = """
    <font size="9" color="#666666">
    <b>Terms & Conditions:</b><br/>
    1. Payment is due within 30 days of invoice date.<br/>
    2. Late payments may be subject to late fees.<br/>
    3. All amounts are in USD unless otherwise specified.<br/><br/>
    Thank you for your excellent service!
    </font>
    """
    content.append(Paragraph(footer_text, normal_style))
    
    # Build PDF
    doc.build(content)
    buffer.seek(0)
    return buffer

def generate_report_pdf(report):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=HexColor('#1E3A8A'),
        alignment=TA_CENTER,
        spaceAfter=12
    )
    
    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=HexColor('#3B82F6'),
        spaceBefore=12,
        spaceAfter=6
    )
    
    normal_style = ParagraphStyle(
        'ReportNormal',
        parent=styles['Normal'],
        fontSize=10,
        leading=14
    )
    
    content = []
    
    # Title
    title = f"<b>Event Report</b><br/>"
    title += f"<font size='14'>{report.event_assignment.event.name}</font><br/>"
    title += f"<font size='12'>Submitted by: {report.event_assignment.team_member.user.get_full_name()}</font>"
    content.append(Paragraph(title, title_style))
    content.append(Spacer(1, 20))
    
    # Report Details Table
    details_data = [
        ['<b>Report ID:</b>', f"#{report.id:06d}", '<b>Submitted:</b>', report.submitted_at.strftime('%Y-%m-%d')],
        ['<b>Event:</b>', report.event_assignment.event.name, '<b>Location:</b>', report.event_assignment.event.location],
        ['<b>Team Member:</b>', report.event_assignment.team_member.user.get_full_name(), '<b>Role:</b>', 'Team Lead' if report.event_assignment.is_team_lead else 'Team Member'],
        ['<b>Attendance Hours:</b>', f"{report.attendance_hours} hours", '<b>Report Status:</b>', f"<font color='{'#065F46' if report.status == 'approved' else '#92400E' if report.status == 'pending' else '#991B1B'}'>{report.get_status_display()}</font>"],
    ]
    
    details_table = Table(details_data, colWidths=[1.2*inch, 2*inch, 1.2*inch, 2*inch])
    details_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    content.append(details_table)
    content.append(Spacer(1, 20))
    
    # Work Summary
    content.append(Paragraph("<b>Work Summary</b>", section_style))
    content.append(Paragraph(report.work_summary, normal_style))
    content.append(Spacer(1, 12))
    
    # Challenges Faced
    if report.challenges_faced:
        content.append(Paragraph("<b>Challenges Faced</b>", section_style))
        content.append(Paragraph(report.challenges_faced, normal_style))
        content.append(Spacer(1, 12))
    
    # Suggestions
    if report.suggestions:
        content.append(Paragraph("<b>Suggestions for Improvement</b>", section_style))
        content.append(Paragraph(report.suggestions, normal_style))
        content.append(Spacer(1, 12))
    
    # Review Section (if reviewed)
    if report.reviewed_by:
        content.append(Paragraph("<b>Review Details</b>", section_style))
        review_data = [
            f"<b>Reviewed by:</b> {report.reviewed_by.get_full_name()}",
            f"<b>Review date:</b> {report.reviewed_at.strftime('%Y-%m-%d %H:%M')}",
            f"<b>Review notes:</b> {report.review_notes if report.review_notes else 'No additional notes.'}"
        ]
        
        for item in review_data:
            content.append(Paragraph(item, normal_style))
    
    # Footer
    content.append(Spacer(1, 30))
    footer = Paragraph(
        f"<font size='8' color='#666666'>Generated by Mookh Ticket Validation System on {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}</font>",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=HexColor('#666666'), alignment=TA_CENTER)
    )
    content.append(footer)
    
    # Build PDF
    doc.build(content)
    buffer.seek(0)
    return buffer