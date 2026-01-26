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
        events = Event.objects.filter(
            assignments__team_member=team_member
        ).distinct().order_by('-start_date')
        
        # Calculate counts for statistics
        total_events = events.count()
        upcoming_count = events.filter(status='upcoming').count()
        ongoing_count = events.filter(status='ongoing').count()
        completed_count = events.filter(status='completed').count()
        
    except TeamMember.DoesNotExist:
        events = Event.objects.none()
        total_events = 0
        upcoming_count = 0
        ongoing_count = 0
        completed_count = 0
        messages.warning(request, 'Complete your profile to view events.')
    
    return render(request, 'events/my_events.html', {
        'events': events,
        'total_events': total_events,
        'upcoming_count': upcoming_count,
        'ongoing_count': ongoing_count,
        'completed_count': completed_count,
    })

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
            user_assignment = assignments.filter(team_member=team_member).first()
            is_assigned = user_assignment is not None
            is_team_lead = user_assignment.is_team_lead if user_assignment else False
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

    