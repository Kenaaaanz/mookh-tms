from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, inch
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from django.utils import timezone
import os
from django.conf import settings

def generate_invoice_pdf(invoice):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )
    
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#1E3A8A'),
        spaceAfter=6,
        alignment=TA_LEFT
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor('#64748B'),
        spaceAfter=20,
        alignment=TA_LEFT
    )
    
    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=HexColor('#1E3A8A'),
        spaceBefore=15,
        spaceAfter=10,
        alignment=TA_LEFT,
        borderWidth=0,
        borderColor=HexColor('#E2E8F0'),
        borderPadding=(0, 0, 4, 0),
        borderRadius=0
    )
    
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor('#334155'),
        leading=14,
        alignment=TA_LEFT
    )
    
    small_style = ParagraphStyle(
        'Small',
        parent=styles['Normal'],
        fontSize=8,
        textColor=HexColor('#64748B'),
        leading=12,
        alignment=TA_LEFT
    )
    
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=10,
        textColor=white,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold'
    )
    
    # Header with Logo
    story.append(Paragraph("MOOKH", title_style))
    story.append(Paragraph("Ticket Validation System", subtitle_style))
    story.append(Spacer(1, 10*mm))
    
    # Invoice Title with Background
    invoice_title_data = [[
        Paragraph(f'<font size="16" color="#FFFFFF"><b>INVOICE #{invoice.id:06d}</b></font>', header_style)
    ]]
    invoice_title_table = Table(invoice_title_data, colWidths=[doc.width])
    invoice_title_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#1E3A8A')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(invoice_title_table)
    story.append(Spacer(1, 5*mm))
    
    # Invoice Date and Status
    date_status_data = [
        [f'Date: {invoice.invoice_date.strftime("%B %d, %Y")}', f'Status: {invoice.get_status_display()}'],
        [f'Due Date: {invoice.due_date.strftime("%B %d, %Y")}', f'Payment Method: {invoice.get_payment_method_display()}'],
    ]
    date_status_table = Table(date_status_data, colWidths=[doc.width/2 - 10, doc.width/2 - 10])
    date_status_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#334155')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(date_status_table)
    story.append(Spacer(1, 5*mm))
    
    # Bill To Section
    story.append(Paragraph("BILL TO", section_style))
    
    # Create bill to table
    bill_to_data = [
        ['Company:', 'Mookh Events'],
        ['Attention:', invoice.event_assignment.team_member.user.get_full_name()],
        ['Email:', invoice.event_assignment.team_member.user.email],
        ['Phone:', invoice.event_assignment.team_member.phone],
    ]
    
    # Add M-Pesa number if different from phone
    if invoice.event_assignment.team_member.mpesa_number != invoice.event_assignment.team_member.phone:
        bill_to_data.append(['M-Pesa:', invoice.event_assignment.team_member.mpesa_number])
    
    bill_to_table = Table(bill_to_data, colWidths=[doc.width/4, doc.width*3/4 - 20])
    bill_to_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#334155')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(bill_to_table)
    story.append(Spacer(1, 5*mm))
    
    # Event Details
    story.append(Paragraph("EVENT DETAILS", section_style))
    
    event_data = [
        ['Event:', invoice.event_assignment.event.name],
        ['Location:', invoice.event_assignment.event.location],
        ['Dates:', f'{invoice.event_assignment.event.start_date.strftime("%B %d, %Y")} - {invoice.event_assignment.event.end_date.strftime("%B %d, %Y")}'],
        ['Role:', 'Team Lead' if invoice.event_assignment.is_team_lead else 'Team Member'],
    ]
    
    event_table = Table(event_data, colWidths=[doc.width/4, doc.width*3/4 - 20])
    event_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#334155')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(event_table)
    story.append(Spacer(1, 5*mm))
    
    # Invoice Items
    story.append(Paragraph("INVOICE ITEMS", section_style))
    
    items_data = [
        ['Description', 'Days', 'Rate (KSh)', 'Amount (KSh)'],
        [
            'Event Ticket Validation Services',
            str(invoice.number_of_days),
            f"{invoice.shift_rate:,.2f}",
            f"{invoice.total_amount:,.2f}"
        ]
    ]
    
    items_table = Table(items_data, colWidths=[doc.width*0.4, doc.width*0.15, doc.width*0.2, doc.width*0.2])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#E2E8F0')),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#F8FAFC')),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 5*mm))
    
    # Summary Section
    summary_data = [
        ['Subtotal:', f'KSh {invoice.total_amount:,.2f}'],
        ['Tax (0%):', 'KSh 0.00'],
        ['Total:', f'KSh {invoice.total_amount:,.2f}'],
    ]
    
    summary_table = Table(summary_data, colWidths=[doc.width*0.7, doc.width*0.2])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('FONTNAME', (2, 2), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (2, 2), (-1, -1), 12),
        ('TEXTCOLOR', (2, 2), (-1, -1), HexColor('#1E3A8A')),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 10*mm))
    
    # Payment Instructions
    story.append(Paragraph("PAYMENT INSTRUCTIONS", section_style))
    
    payment_instructions = [
        ['1.', 'Create your invoice after the event'],
        ['2.', 'Submit the Invoice in time'],
        ['3.', f'Be sure to review all your details keenly before submitting the invoice.'],
        ['4.', 'Payment will be made within 2-5 days of invoice submission.'],
        ['5.', 'If you have any questions regarding this invoice, please contact the Team Manager or email support@mookh.com'],
    ]
    
    payment_table = Table(payment_instructions, colWidths=[doc.width*0.1, doc.width*0.8])
    payment_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#334155')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (1, 0), (-1, -1), 0),
    ]))
    story.append(payment_table)
    story.append(Spacer(1, 5*mm))
    
    # Additional Notes (if any)
    if invoice.additional_notes:
        story.append(Paragraph("ADDITIONAL NOTES", section_style))
        notes_style = ParagraphStyle(
            'Notes',
            parent=normal_style,
            backColor=HexColor('#FEF9C3'),
            borderWidth=1,
            borderColor=HexColor('#FDE68A'),
            borderPadding=10,
            borderRadius=5,
            textColor=HexColor('#92400E')
        )
        story.append(Paragraph(invoice.additional_notes, notes_style))
        story.append(Spacer(1, 5*mm))
    
    # Footer
    story.append(Spacer(1, 15*mm))
    
    footer_text = f"""
    <para>
        <font color="#64748B" size="8">
        <b>Terms & Conditions:</b><br/>
        Payment is due within 30 days. Late payments may be subject to late fees.<br/>
        For questions regarding this invoice, please contact accounts@mookh.com<br/><br/>
        Thank you for your excellent service!<br/>
        Generated on {timezone.now().strftime('%B %d, %Y at %H:%M')}
        </font>
    </para>
    """
    story.append(Paragraph(footer_text, small_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_report_pdf(report):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )
    
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#8B5CF6'),
        spaceAfter=6,
        alignment=TA_LEFT
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor('#64748B'),
        spaceAfter=20,
        alignment=TA_LEFT
    )
    
    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=HexColor('#8B5CF6'),
        spaceBefore=15,
        spaceAfter=10,
        alignment=TA_LEFT,
        borderWidth=0,
        borderColor=HexColor('#E2E8F0'),
        borderPadding=(0, 0, 4, 0),
        borderRadius=0
    )
    
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor('#334155'),
        leading=14,
        alignment=TA_LEFT
    )
    
    small_style = ParagraphStyle(
        'Small',
        parent=styles['Normal'],
        fontSize=8,
        textColor=HexColor('#64748B'),
        leading=12,
        alignment=TA_LEFT
    )
    
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=10,
        textColor=white,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold'
    )
    
    quote_style = ParagraphStyle(
        'Quote',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor('#4B5563'),
        alignment=TA_LEFT,
        leftIndent=20,
        rightIndent=20,
        spaceBefore=10,
        spaceAfter=10,
        fontName='Helvetica-Oblique'
    )
    
    # Header with Logo
    story.append(Paragraph("MOOKH", title_style))
    story.append(Paragraph("Event Report", subtitle_style))
    story.append(Spacer(1, 10*mm))
    
    # Report Title with Background
    report_title_data = [[
        Paragraph(f'<font size="16" color="#FFFFFF"><b>EVENT REPORT #{report.id:06d}</b></font>', header_style)
    ]]
    report_title_table = Table(report_title_data, colWidths=[doc.width])
    report_title_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#8B5CF6')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(report_title_table)
    story.append(Spacer(1, 5*mm))
    
    # Report Metadata
    meta_data = [
        ['Submitted By:', report.event_assignment.team_member.user.get_full_name()],
        ['Submitted On:', report.submitted_at.strftime('%B %d, %Y at %H:%M')],
        ['Status:', report.get_status_display()],
    ]
    
    if report.reviewed_by:
        meta_data.append(['Reviewed By:', report.reviewed_by.get_full_name()])
        meta_data.append(['Reviewed On:', report.reviewed_at.strftime('%B %d, %Y at %H:%M')])
    
    meta_table = Table(meta_data, colWidths=[doc.width*0.2, doc.width*0.7])
    meta_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#334155')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 5*mm))
    
    # Status Badge
    status_color = {
        'pending': '#F59E0B',
        'approved': '#10B981',
        'rejected': '#EF4444'
    }.get(report.status, '#6B7280')
    
    status_data = [[
        Paragraph(
            f'<font color="{status_color}" size="10"><b>● {report.get_status_display().upper()}</b></font>',
            normal_style
        )
    ]]
    status_table = Table(status_data, colWidths=[doc.width])
    status_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#F8FAFC')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(status_table)
    story.append(Spacer(1, 5*mm))
    
    # Event Details
    story.append(Paragraph("EVENT INFORMATION", section_style))
    
    event_data = [
        ['Event Name:', report.event_assignment.event.name],
        ['Location:', report.event_assignment.event.location],
        ['Event Dates:', f'{report.event_assignment.event.start_date.strftime("%B %d, %Y")} - {report.event_assignment.event.end_date.strftime("%B %d, %Y")}'],
        ['Attendance Hours:', f'{report.attendance_hours} hours'],
        ['Role:', 'Team Lead' if report.event_assignment.is_team_lead else 'Team Member'],
    ]
    
    event_table = Table(event_data, colWidths=[doc.width*0.25, doc.width*0.65])
    event_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#334155')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#E2E8F0')),
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#F8FAFC')),
    ]))
    story.append(event_table)
    story.append(Spacer(1, 5*mm))
    
    # Work Summary
    story.append(Paragraph("WORK SUMMARY", section_style))
    story.append(Paragraph(report.work_summary.replace('\n', '<br/>'), normal_style))
    story.append(Spacer(1, 5*mm))
    
    # Challenges Faced
    if report.challenges_faced:
        story.append(Paragraph("CHALLENGES FACED", section_style))
        story.append(Paragraph(report.challenges_faced.replace('\n', '<br/>'), normal_style))
        story.append(Spacer(1, 5*mm))
    
    # Suggestions
    if report.suggestions:
        story.append(Paragraph("SUGGESTIONS FOR IMPROVEMENT", section_style))
        story.append(Paragraph(report.suggestions.replace('\n', '<br/>'), normal_style))
        story.append(Spacer(1, 5*mm))
    
    # Review Information
    if report.reviewed_by:
        story.append(Paragraph("REVIEW INFORMATION", section_style))
        
        review_data = [
            ['Reviewed By:', report.reviewed_by.get_full_name()],
            ['Review Date:', report.reviewed_at.strftime('%B %d, %Y at %H:%M')],
        ]
        
        if report.review_notes:
            review_data.append(['Review Notes:', report.review_notes])
        
        review_table = Table(review_data, colWidths=[doc.width*0.2, doc.width*0.7])
        review_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#334155')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(review_table)
        story.append(Spacer(1, 5*mm))
    
    # Team Member Information
    story.append(Paragraph("TEAM MEMBER INFORMATION", section_style))
    
    member_data = [
        ['Name:', report.event_assignment.team_member.user.get_full_name()],
        ['Email:', report.event_assignment.team_member.user.email],
        ['Phone:', report.event_assignment.team_member.phone],
        ['M-Pesa Number:', report.event_assignment.team_member.mpesa_number],
        ['ID Number:', report.event_assignment.team_member.id_number or 'Not provided'],
    ]
    
    member_table = Table(member_data, colWidths=[doc.width*0.25, doc.width*0.65])
    member_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#334155')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#E2E8F0')),
    ]))
    story.append(member_table)
    story.append(Spacer(1, 10*mm))
    
    # Footer
    footer_text = f"""
    <para>
        <font color="#64748B" size="8">
        This report has been automatically generated by the Mookh Ticket Validation System.<br/>
        For verification, please contact admin@mookh.com<br/><br/>
        Generated on {timezone.now().strftime('%B %d, %Y at %H:%M')}
        </font>
    </para>
    """
    story.append(Paragraph(footer_text, small_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer