from django.db import models
from django.contrib.auth.models import User
from teams.models import TeamMember

class Event(models.Model):
    EVENT_STATUS = (
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=EVENT_STATUS, default='upcoming')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class EventAssignment(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='assignments')
    team_member = models.ForeignKey(TeamMember, on_delete=models.CASCADE, related_name='event_assignments')
    is_team_lead = models.BooleanField(default=False)
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['event', 'team_member']
    
    def __str__(self):
        return f"{self.team_member.user.get_full_name()} - {self.event.name}"