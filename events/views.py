from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from .models import Event, EventAssignment
from teams.models import TeamMember
from invoices.models import Invoice, EventReport
from .forms import EventForm, EventAssignmentForm
from django.http import JsonResponse

@login_required
@user_passes_test(lambda u: u.is_staff)
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('event_detail', event_id=event.id)
    else:
        form = EventForm()
    
    return render(request, 'events/create_event.html', {'form': form})

@login_required
def event_list(request):
    events = Event.objects.all().order_by('-start_date')
    return render(request, 'events/event_list.html', {'events': events})

@login_required
def my_events(request):
    try:
        team_member = TeamMember.objects.get(user=request.user)
        
        # Get all events the user is assigned to
        events = Event.objects.filter(
            assignments__team_member=team_member
        ).distinct().order_by('-start_date')
        
        # Annotate each event with the user's specific assignment
        for event in events:
            event.user_assignments = EventAssignment.objects.filter(
                event=event,
                team_member=team_member
            ).select_related(
                'report',
                'team_member__user'
            ).prefetch_related('invoices').first()
        
        # Calculate counts
        upcoming_count = events.filter(status='upcoming').count()
        ongoing_count = events.filter(status='ongoing').count()
        completed_count = events.filter(status='completed').count()
        
        context = {
            'events': events,
            'team_member': team_member,
            'upcoming_count': upcoming_count,
            'ongoing_count': ongoing_count,
            'completed_count': completed_count,
        }
    except TeamMember.DoesNotExist:
        events = Event.objects.none()
        context = {
            'events': events,
            'team_member': None,
            'upcoming_count': 0,
            'ongoing_count': 0,
            'completed_count': 0,
        }
        messages.warning(request, 'Complete your profile to view events.')
    
    return render(request, 'events/my_events.html', context)

@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    assignments = event.assignments.all().select_related('team_member__user')
    
    # Check if user is team member for this event
    is_assigned = False
    is_team_lead = False
    user_assignment = None
    
    if not request.user.is_staff:
        try:
            team_member = TeamMember.objects.get(user=request.user)
            # Fix: Filter by team_member_id or team_member field properly
            user_assignment = assignments.filter(team_member_id=team_member.id).first()
            # OR:
            # user_assignment = assignments.filter(team_member=team_member).first()
            
            if user_assignment:
                is_assigned = True
                is_team_lead = user_assignment.is_team_lead
        except TeamMember.DoesNotExist:
            pass
    
    # Get reports and invoices for this event
    reports = EventReport.objects.filter(event_assignment__event=event)
    invoices = Invoice.objects.filter(event_assignment__event=event)
    
    context = {
        'event': event,
        'assignments': assignments,
        'reports': reports,
        'invoices': invoices,
        'is_assigned': is_assigned,
        'is_team_lead': is_team_lead,
        'user_assignment': user_assignment,
    }
    
    return render(request, 'events/event_detail.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def assign_team_members(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        form = EventAssignmentForm(request.POST, event=event)
        if form.is_valid():
            team_members = form.cleaned_data['team_members']
            team_lead = form.cleaned_data['team_lead']
            
            # Clear existing assignments
            EventAssignment.objects.filter(event=event).delete()
            
            # Create new assignments
            for team_member in team_members:
                is_lead = (team_member == team_lead)
                EventAssignment.objects.create(
                    event=event,
                    team_member=team_member,
                    is_team_lead=is_lead
                )
            
            messages.success(request, 'Team members assigned successfully!')
            return redirect('event_detail', event_id=event.id)
    else:
        form = EventAssignmentForm(event=event)
    
    # Get currently assigned team members
    assigned_members = event.assignments.all()
    
    return render(request, 'events/assign_team.html', {
        'event': event,
        'form': form,
        'assigned_members': assigned_members,
    })

from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import Event, EventAssignment
from invoices.models import Invoice, EventReport

@staff_member_required
def event_assignments(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    assignments = EventAssignment.objects.filter(event=event).select_related('team_member__user')
    
    context = {
        'event': event,
        'assignments': assignments,
        'title': f'Team Assignments - {event.name}',
        'opts': event._meta,
        'original': event,
        'is_popup': False,
        'save_as': False,
        'has_delete_permission': True,
        'has_add_permission': True,
        'has_change_permission': True,
        'has_view_permission': True,
        'has_absolute_url': False,
    }
    return render(request, 'admin/events/event/assignments.html', context)

@staff_member_required
def event_reports_invoices(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    assignments = EventAssignment.objects.filter(event=event).select_related('team_member__user')
    
    reports = EventReport.objects.filter(event_assignment__event=event).select_related(
        'event_assignment__team_member__user',
        'event_assignment__event'
    )
    
    invoices = Invoice.objects.filter(event_assignment__event=event).select_related(
        'event_assignment__team_member__user',
        'event_assignment__event'
    )
    
    context = {
        'event': event,
        'assignments': assignments,
        'reports': reports,
        'invoices': invoices,
        'title': f'Reports & Invoices - {event.name}',
        'opts': event._meta,
        'original': event,
    }
    return render(request, 'admin/events/event/reports_invoices.html', context)
    