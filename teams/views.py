from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import login, logout
from .models import TeamMember
from events.models import EventAssignment, Event
from invoices.models import Invoice, EventReport
from django.db.models import Q
from .forms import TeamMemberForm, TeamMemberRegistrationForm
from django.contrib.auth.models import User
from django.utils import timezone

def register(request):
    if request.method == 'POST':
        form = TeamMemberRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Auto-login after registration
            login(request, user)
            
            messages.success(request, 
                'Registration successful! Your account is pending verification. '
                'You can update your profile and start applying for events once verified.'
            )
            
            # Redirect to profile setup
            return redirect('profile')
    else:
        form = TeamMemberRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard(request):
    user = request.user
    context = {}
    
    if user.is_staff:
        # Admin dashboard
        total_events = Event.objects.count()
        upcoming_events = Event.objects.filter(status='upcoming').count()
        total_team_members = TeamMember.objects.count()
        verified_members = TeamMember.objects.filter(is_verified=True).count()
        pending_invoices = Invoice.objects.filter(status='submitted').count()
        pending_reports = EventReport.objects.filter(status='pending').count()
        completed_invoices = Invoice.objects.filter(status='paid').count()
        
        context.update({
            'total_events': total_events,
            'upcoming_events': upcoming_events,
            'total_team_members': total_team_members,
            'verified_members': verified_members,
            'pending_invoices': pending_invoices,
            'pending_reports': pending_reports,
            'completed_invoices': completed_invoices,
            'recent_events': Event.objects.order_by('-start_date')[:5],
            'recent_invoices': Invoice.objects.filter(status='submitted').order_by('-created_at')[:5],
            'recent_reports': EventReport.objects.filter(status='pending').order_by('-submitted_at')[:5],
            'active_users': User.objects.filter(is_active=True).count(),
        })
        
        # If accessing from admin, use admin dashboard template
        if request.path.startswith('/admin/'):
            return render(request, 'admin/index.html', context)
        else:
            return render(request, 'admin_dashboard.html', context)
    else:
        # Team member dashboard
        try:
            team_member = TeamMember.objects.get(user=user)
            assignments = EventAssignment.objects.filter(team_member=team_member)
            
            my_events = Event.objects.filter(
                assignments__team_member=team_member
            ).distinct().order_by('-start_date')
            
            my_invoices = Invoice.objects.filter(
                event_assignment__team_member=team_member
            ).order_by('-created_at')
            
            my_reports = EventReport.objects.filter(
                event_assignment__team_member=team_member
            ).order_by('-submitted_at')
            
            context.update({
                'team_member': team_member,
                'my_events': my_events[:5],
                'my_invoices': my_invoices[:5],
                'my_reports': my_reports[:5],
                'total_events': my_events.count(),
                'completed_invoices': my_invoices.filter(status='paid').count(),
                'pending_reports': my_reports.filter(status='pending').count(),
                'upcoming_events': my_events.filter(status='upcoming')[:3],
            })
        except TeamMember.DoesNotExist:
            messages.warning(request, 'Please complete your profile setup.')
            return redirect('profile')
        template = 'team_dashboard.html'
    
    return render(request, template, context)

@login_required
def profile_view(request):
    try:
        team_member = TeamMember.objects.get(user=request.user)
    except TeamMember.DoesNotExist:
        team_member = None
    
    if request.method == 'POST':
        form = TeamMemberForm(request.POST, instance=team_member)
        if form.is_valid():
            team_member = form.save(commit=False)
            team_member.user = request.user
            team_member.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = TeamMemberForm(instance=team_member)
    
    return render(request, 'profile.html', {'form': form})

@login_required
def custom_logout(request):
    """Custom logout view with additional functionality"""
    # You can add any pre-logout actions here
    # For example: logging logout activity, clearing session data, etc.
    
    # Store user info before logout if needed (for logging)
    user_info = {
        'username': request.user.username,
        'email': request.user.email,
        'logout_time': timezone.now()
    }
    
    # Perform logout
    logout(request)
    
    # Render logout confirmation page
    return render(request, 'registration/logout.html')

from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from .models import TeamMember
from events.models import EventAssignment
from invoices.models import Invoice, EventReport

@staff_member_required
def team_member_payment(request, member_id):
    team_member = get_object_or_404(TeamMember, id=member_id)
    
    context = {
        'team_member': team_member,
        'title': f'Payment Information - {team_member.user.get_full_name()}',
        'opts': team_member._meta,
        'original': team_member,
    }
    return render(request, 'admin/teams/teammember/payment.html', context)

@staff_member_required
def team_member_verification(request, member_id):
    team_member = get_object_or_404(TeamMember, id=member_id)
    
    # Get statistics
    events_count = EventAssignment.objects.filter(team_member=team_member).count()
    reports_count = EventReport.objects.filter(event_assignment__team_member=team_member).count()
    invoices_count = Invoice.objects.filter(event_assignment__team_member=team_member).count()
    recent_events = EventAssignment.objects.filter(team_member=team_member).select_related('event')[:5]
    
    context = {
        'team_member': team_member,
        'events_count': events_count,
        'reports_count': reports_count,
        'invoices_count': invoices_count,
        'recent_events': recent_events,
        'title': f'Verification Status - {team_member.user.get_full_name()}',
        'opts': team_member._meta,
        'original': team_member,
    }
    return render(request, 'admin/teams/teammember/verification.html', context)

@staff_member_required
def team_member_activity(request, member_id):
    team_member = get_object_or_404(TeamMember, id=member_id)
    
    assignments = EventAssignment.objects.filter(team_member=team_member).select_related('event')
    reports = EventReport.objects.filter(event_assignment__team_member=team_member).select_related('event_assignment__event')
    invoices = Invoice.objects.filter(event_assignment__team_member=team_member).select_related('event_assignment__event')
    
    context = {
        'team_member': team_member,
        'assignments': assignments,
        'reports': reports,
        'invoices': invoices,
        'title': f'Activity Log - {team_member.user.get_full_name()}',
        'opts': team_member._meta,
        'original': team_member,
    }
    return render(request, 'admin/teams/teammember/activity.html', context)