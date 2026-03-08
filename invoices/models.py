from django.db import models
from events.models import Event, EventAssignment
from teams.models import TeamMember
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User

class EventReport(models.Model):
    REPORT_STATUS = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    event_assignment = models.OneToOneField(EventAssignment, on_delete=models.CASCADE, related_name='report')
    report_content = models.TextField(blank=True)
    attendance_hours = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    work_summary = models.TextField()
    challenges_faced = models.TextField(blank=True)
    suggestions = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=REPORT_STATUS, default='pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Report - {self.event_assignment.team_member.user.get_full_name()} - {self.event_assignment.event.name}"

class Invoice(models.Model):
    INVOICE_STATUS = (
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('verified', 'Verified'),
        ('paid', 'Paid'),
        ('rejected', 'Rejected'),
    )
    
    PAYMENT_METHOD = (
        ('mpesa', 'M-Pesa'),
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
    )
    
    event_assignment = models.ForeignKey(EventAssignment, on_delete=models.CASCADE, related_name='invoices')
    number_of_days = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)
    shift_rate = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD, default='mpesa')
    mpesa_transaction_id = models.CharField(max_length=50, blank=True, null=True)
    mpesa_confirmation_code = models.CharField(max_length=50, blank=True, null=True)
    additional_notes = models.TextField(blank=True)
    invoice_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=INVOICE_STATUS, default='draft')
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        self.total_amount = self.number_of_days * self.shift_rate
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Invoice #{self.id} - {self.event_assignment.team_member.user.get_full_name()}"