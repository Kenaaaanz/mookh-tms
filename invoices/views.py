from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from .models import Invoice, EventReport
from events.models import EventAssignment
from teams.models import TeamMember
from .forms import InvoiceForm, EventReportForm, InvoiceVerificationForm, ReportReviewForm
from .utils import generate_invoice_pdf, generate_report_pdf
from django.db.models import Q

@login_required
def my_invoices(request):
    try:
        team_member = TeamMember.objects.get(user=request.user)
        invoices = Invoice.objects.filter(
            event_assignment__team_member=team_member
        ).order_by('-created_at')
    except TeamMember.DoesNotExist:
        invoices = Invoice.objects.none()
    
    return render(request, 'invoices/my_invoices.html', {'invoices': invoices})

@login_required
def my_reports(request):
    try:
        team_member = TeamMember.objects.get(user=request.user)
        reports = EventReport.objects.filter(
            event_assignment__team_member=team_member
        ).order_by('-submitted_at')
        
        # Calculate counts
        total_reports = reports.count()
        approved_count = reports.filter(status='approved').count()
        pending_count = reports.filter(status='pending').count()
        
    except TeamMember.DoesNotExist:
        reports = EventReport.objects.none()
        total_reports = 0
        approved_count = 0
        pending_count = 0
    
    return render(request, 'invoices/my_reports.html', {
        'reports': reports,
        'total_reports': total_reports,
        'approved_count': approved_count,
        'pending_count': pending_count,
    })

@login_required
def create_invoice(request, assignment_id):
    assignment = get_object_or_404(EventAssignment, id=assignment_id)
    
    # Check if user is authorized
    if not (request.user.is_staff or assignment.team_member.user == request.user):
        messages.error(request, 'You are not authorized to create invoices for this assignment.')
        return redirect('dashboard')
    
    # Check if invoice already exists
    if Invoice.objects.filter(event_assignment=assignment).exists():
        messages.warning(request, 'An invoice already exists for this assignment.')
        return redirect('event_detail', event_id=assignment.event.id)
    
    if request.method == 'POST':
        form = InvoiceForm(request.POST, assignment=assignment)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.event_assignment = assignment
            invoice.save()
            
            messages.success(request, 'Invoice created successfully!')
            return redirect('event_detail', event_id=assignment.event.id)
    else:
        initial_data = {
            'number_of_days': 1,
            'shift_rate': assignment.team_member.shift_rate if assignment.team_member.shift_rate > 0 else 1000,
            'due_date': timezone.now().date() + timezone.timedelta(days=30),
            'payment_method': 'mpesa',
        }
        form = InvoiceForm(initial=initial_data, assignment=assignment)
    
    return render(request, 'invoices/create_invoice.html', {
        'form': form,
        'assignment': assignment,
    })

@login_required
def create_report(request, assignment_id):
    assignment = get_object_or_404(EventAssignment, id=assignment_id)
    
    # Check if user is authorized
    if not (request.user.is_staff or assignment.team_member.user == request.user):
        messages.error(request, 'You are not authorized to create reports for this assignment.')
        return redirect('dashboard')
    
    # Check if report already exists
    if EventReport.objects.filter(event_assignment=assignment).exists():
        messages.warning(request, 'A report already exists for this assignment.')
        return redirect('event_detail', event_id=assignment.event.id)
    
    if request.method == 'POST':
        form = EventReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.event_assignment = assignment
            report.save()
            
            messages.success(request, 'Report submitted successfully!')
            return redirect('event_detail', event_id=assignment.event.id)
    else:
        form = EventReportForm()
    
    return render(request, 'invoices/create_report.html', {
        'form': form,
        'assignment': assignment,
    })

@login_required
def download_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    # Check authorization
    if not (request.user.is_staff or invoice.event_assignment.team_member.user == request.user):
        messages.error(request, 'You are not authorized to download this invoice.')
        return redirect('dashboard')
    
    buffer = generate_invoice_pdf(invoice)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.id}.pdf"'
    return response

@login_required
def download_report(request, report_id):
    report = get_object_or_404(EventReport, id=report_id)
    
    # Check authorization
    if not (request.user.is_staff or report.event_assignment.team_member.user == request.user):
        messages.error(request, 'You are not authorized to download this report.')
        return redirect('dashboard')
    
    buffer = generate_report_pdf(report)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="report_{report.id}.pdf"'
    return response

@login_required
@user_passes_test(lambda u: u.is_staff)
def verify_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    if request.method == 'POST':
        form = InvoiceVerificationForm(request.POST, instance=invoice)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.verified_by = request.user
            invoice.verified_at = timezone.now()
            invoice.is_verified = True
            invoice.save()
            
            messages.success(request, 'Invoice verified successfully!')
            return redirect('event_detail', event_id=invoice.event_assignment.event.id)
    else:
        form = InvoiceVerificationForm(instance=invoice)
    
    return render(request, 'invoices/verify_invoice.html', {
        'form': form,
        'invoice': invoice,
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def review_report(request, report_id):
    report = get_object_or_404(EventReport, id=report_id)
    
    if request.method == 'POST':
        form = ReportReviewForm(request.POST, instance=report)
        if form.is_valid():
            report = form.save(commit=False)
            report.reviewed_by = request.user
            report.reviewed_at = timezone.now()
            report.save()
            
            messages.success(request, 'Report reviewed successfully!')
            return redirect('event_detail', event_id=report.event_assignment.event.id)
    else:
        form = ReportReviewForm(instance=report)
    
    return render(request, 'invoices/review_report.html', {
        'form': form,
        'report': report,
    })

@login_required
def submit_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    # Check if user is authorized
    if not (request.user.is_staff or invoice.event_assignment.team_member.user == request.user):
        messages.error(request, 'You are not authorized to submit this invoice.')
        return redirect('dashboard')
    
    # Check if invoice can be submitted
    if invoice.status != 'draft':
        messages.warning(request, f'This invoice is already {invoice.get_status_display().lower()}.')
        return redirect('my_invoices')
    
    # Submit the invoice
    invoice.status = 'submitted'
    invoice.save()
    
    # Log the submission
    messages.success(request, f'Invoice #{invoice.id} submitted successfully for verification.')
    
    # Send notification to admin (you can implement email notification here)
    
    return redirect('my_invoices')

@login_required
def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    # Check authorization
    if not (request.user.is_staff or invoice.event_assignment.team_member.user == request.user):
        messages.error(request, 'You are not authorized to view this invoice.')
        return redirect('dashboard')
    
    return render(request, 'invoices/invoice_detail.html', {
        'invoice': invoice,
    })

from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from .models import Invoice, EventReport

@staff_member_required
def invoice_admin_details(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    context = {
        'invoice': invoice,
        'title': f'Invoice #{invoice.id} Details',
        'opts': invoice._meta,
        'original': invoice,
    }
    return render(request, 'admin/invoices/invoice/details.html', context)

@staff_member_required
def report_admin_details(request, report_id):
    report = get_object_or_404(EventReport, id=report_id)
    
    context = {
        'report': report,
        'title': f'Report #{report.id} Details',
        'opts': report._meta,
        'original': report,
    }
    return render(request, 'admin/invoices/report/details.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from .models import Invoice, EventReport
from events.models import EventAssignment
from teams.models import TeamMember
from .forms import InvoiceForm, EventReportForm, InvoiceVerificationForm, ReportReviewForm
from .utils import generate_invoice_pdf, generate_report_pdf
from django.db.models import Q

@login_required
@user_passes_test(lambda u: u.is_staff)
def review_report_action(request, report_id, action):
    """
    Handle approve/reject actions for reports
    """
    report = get_object_or_404(EventReport, id=report_id)
    
    if action == 'approve':
        report.status = 'approved'
        report.reviewed_by = request.user
        report.reviewed_at = timezone.now()
        messages.success(request, f'Report #{report.id} has been approved successfully.')
    elif action == 'reject':
        report.status = 'rejected'
        report.reviewed_by = request.user
        report.reviewed_at = timezone.now()
        messages.warning(request, f'Report #{report.id} has been rejected.')
    else:
        messages.error(request, 'Invalid action.')
        return redirect('admin:invoices_eventreport_change', report_id)
    
    report.save()
    return redirect(f'/admin/invoices/eventreport/{report.id}/change/#review-information-tab')


@login_required
def report_detail_view(request, report_id):
    """
    Public view for report details
    """
    report = get_object_or_404(EventReport, id=report_id)
    
    # Check authorization
    if not (request.user.is_staff or report.event_assignment.team_member.user == request.user):
        messages.error(request, 'You are not authorized to view this report.')
        return redirect('dashboard')
    
    context = {
        'report': report,
        'event': report.event_assignment.event,
        'team_member': report.event_assignment.team_member,
        'is_team_lead': report.event_assignment.is_team_lead,
    }
    
    return render(request, 'invoices/report_detail.html', context)


@login_required
def report_review_notes(request, report_id):
    """
    AJAX view to add review notes
    """
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    if request.method == 'POST':
        report = get_object_or_404(EventReport, id=report_id)
        notes = request.POST.get('review_notes', '')
        
        report.review_notes = notes
        report.save()
        
        return JsonResponse({
            'success': True,
            'notes': notes,
            'reviewed_by': request.user.get_full_name(),
            'reviewed_at': timezone.now().strftime('%B %d, %Y %H:%M')
        })
    
    return JsonResponse({'error': 'Invalid method'}, status=405)


@login_required
def report_timeline(request, report_id):
    """
    AJAX view to get report timeline
    """
    report = get_object_or_404(EventReport, id=report_id)
    
    timeline = [
        {
            'date': report.submitted_at.isoformat(),
            'action': 'submitted',
            'description': 'Report submitted by team member',
            'user': report.event_assignment.team_member.user.get_full_name()
        }
    ]
    
    if report.reviewed_at:
        timeline.append({
            'date': report.reviewed_at.isoformat(),
            'action': report.status,
            'description': f'Report {report.get_status_display().lower()} by admin',
            'user': report.reviewed_by.get_full_name() if report.reviewed_by else 'System'
        })
    
    return JsonResponse({'timeline': timeline})