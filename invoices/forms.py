from django import forms
from django.utils import timezone
from .models import Invoice, EventReport

class InvoiceForm(forms.ModelForm):
    shift_rate = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={'step': '100'})
    )
    
    class Meta:
        model = Invoice
        fields = ['number_of_days', 'shift_rate', 'payment_method', 'additional_notes', 'due_date']
        widgets = {
            'additional_notes': forms.Textarea(attrs={'rows': 3}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'number_of_days': forms.NumberInput(attrs={'min': 1, 'step': 0.5}),
        }
    
    def __init__(self, *args, **kwargs):
        self.assignment = kwargs.pop('assignment', None)
        super().__init__(*args, **kwargs)
        
        if self.assignment and hasattr(self.assignment, 'team_member'):
            team_member = self.assignment.team_member
            if hasattr(team_member, 'shift_rate') and team_member.shift_rate:
                self.fields['shift_rate'].initial = team_member.shift_rate
    
    def clean_number_of_days(self):
        days = self.cleaned_data.get('number_of_days')
        if days is None or days <= 0:
            raise forms.ValidationError("Number of days must be greater than 0.")
        if days > 365:
            raise forms.ValidationError("Number of days cannot exceed 365.")
        return days
    
    def clean_shift_rate(self):
        shift_rate = self.cleaned_data.get('shift_rate')
        if shift_rate is None or shift_rate <= 0:
            raise forms.ValidationError("shift rate must be greater than 0.")
        return shift_rate
    
    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date and due_date < timezone.now().date():
            raise forms.ValidationError("Due date cannot be in the past.")
        return due_date


class EventReportForm(forms.ModelForm):
    class Meta:
        model = EventReport
        fields = ['attendance_hours', 'work_summary', 'challenges_faced', 'suggestions']
        widgets = {
            'work_summary': forms.Textarea(attrs={'rows': 4}),
            'challenges_faced': forms.Textarea(attrs={'rows': 3}),
            'suggestions': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_attendance_hours(self):
        hours = self.cleaned_data.get('attendance_hours')
        if hours <= 0:
            raise forms.ValidationError("Attendance hours must be greater than 0.")
        return hours


class InvoiceVerificationForm(forms.ModelForm):
    mpesa_transaction_id = forms.CharField(
        required=False,
        help_text="Enter M-Pesa transaction ID if payment was made"
    )
    mpesa_confirmation_code = forms.CharField(
        required=False,
        help_text="Enter M-Pesa confirmation code"
    )
    
    class Meta:
        model = Invoice
        fields = ['status', 'payment_method', 'mpesa_transaction_id', 
                 'mpesa_confirmation_code', 'paid_at']
        widgets = {
            'paid_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].choices = [
            ('verified', 'Verified'),
            ('paid', 'Paid'),
            ('rejected', 'Rejected'),
        ]


class ReportReviewForm(forms.ModelForm):
    class Meta:
        model = EventReport
        fields = ['status', 'review_notes']
        widgets = {
            'review_notes': forms.Textarea(attrs={'rows': 4}),
        }