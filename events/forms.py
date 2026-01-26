from django import forms
from .models import Event, EventAssignment
from teams.models import TeamMember
from django.utils import timezone

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'location', 'start_date', 'end_date', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if start_date >= end_date:
                raise forms.ValidationError("End date must be after start date.")
            
            if start_date < timezone.now():
                raise forms.ValidationError("Start date cannot be in the past.")
        
        return cleaned_data

class EventAssignmentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event', None)
        super().__init__(*args, **kwargs)
        
        # Only show verified team members
        team_members = TeamMember.objects.filter(is_verified=True)
        
        self.fields['team_members'] = forms.ModelMultipleChoiceField(
            queryset=team_members,
            widget=forms.CheckboxSelectMultiple,
            required=True,
            label="Select Team Members"
        )
        
        self.fields['team_lead'] = forms.ModelChoiceField(
            queryset=team_members,
            required=True,
            label="Select Team Lead"
        )
    
    def clean(self):
        cleaned_data = super().clean()
        team_members = cleaned_data.get('team_members', [])
        team_lead = cleaned_data.get('team_lead')
        
        if team_lead and team_lead not in team_members:
            raise forms.ValidationError("Team lead must be one of the selected team members.")
        
        return cleaned_data