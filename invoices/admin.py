from django.utils import timezone
from django.contrib import admin, messages
from .models import Invoice, EventReport

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'event_assignment', 'number_of_days', 'daily_rate', 
                   'total_amount', 'payment_method', 'status', 'is_verified', 'invoice_date']
    list_filter = ['status', 'is_verified', 'payment_method', 'invoice_date']
    search_fields = ['mpesa_transaction_id', 'mpesa_confirmation_code',
                    'event_assignment__event__name',
                    'event_assignment__team_member__user__username']
    readonly_fields = ['total_amount', 'created_at']
    actions = ['mark_as_paid', 'mark_as_verified']
    
    fieldsets = (
        ('Invoice Details', {
            'fields': ('event_assignment', 'number_of_days', 'daily_rate', 'total_amount')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'mpesa_transaction_id', 'mpesa_confirmation_code', 'paid_at')
        }),
        ('Additional Information', {
            'fields': ('additional_notes', 'invoice_date', 'due_date')
        }),
        ('Status', {
            'fields': ('status', 'is_verified', 'verified_by', 'verified_at', 'created_at')
        }),
    )
    
    def mark_as_paid(self, request, queryset):
        """Admin action to mark selected invoices as paid"""
        updated = queryset.update(status='paid')
        self.message_user(
            request, 
            f'Marked {updated} invoice(s) as paid.',
            messages.SUCCESS
        )
    mark_as_paid.short_description = "Mark selected invoices as paid"
    
    def mark_as_verified(self, request, queryset):
        """Admin action to mark selected invoices as verified"""
        updated = queryset.update(is_verified=True, verified_by=request.user, verified_at=timezone.now())
        self.message_user(
            request, 
            f'Verified {updated} invoice(s).',
            messages.SUCCESS
        )
    mark_as_verified.short_description = "Verify selected invoices"
    
    def get_readonly_fields(self, request, obj=None):
        """Make certain fields read-only based on object state"""
        readonly_fields = list(self.readonly_fields)
        if obj and obj.is_verified:
            readonly_fields.extend(['daily_rate', 'number_of_days', 'event_assignment'])
        return readonly_fields
    
    def get_queryset(self, request):
        """Optimize queryset for admin display"""
        queryset = super().get_queryset(request)
        queryset = queryset.select_related(
            'event_assignment',
            'event_assignment__event',
            'event_assignment__team_member',
            'event_assignment__team_member__user',
            'verified_by'
        )
        return queryset


@admin.register(EventReport)
class EventReportAdmin(admin.ModelAdmin):
    list_display = ['event_assignment', 'status', 'attendance_hours', 'submitted_at', 'reviewed_by']
    list_filter = ['status', 'submitted_at']
    search_fields = ['event_assignment__event__name', 
                    'event_assignment__team_member__user__username',
                    'work_summary']
    readonly_fields = ['submitted_at']
    actions = ['approve_selected_reports', 'reject_selected_reports']
    
    fieldsets = (
        ('Report Details', {
            'fields': ('event_assignment', 'attendance_hours', 'work_summary')
        }),
        ('Additional Information', {
            'fields': ('challenges_faced', 'suggestions')
        }),
        ('Review Information', {
            'fields': ('status', 'review_notes', 'reviewed_by', 'reviewed_at', 'submitted_at')
        }),
    )
    
    def approve_selected_reports(self, request, queryset):
        """Admin action to approve selected reports"""
        updated = queryset.update(
            status='approved', 
            reviewed_by=request.user, 
            reviewed_at=timezone.now()
        )
        self.message_user(
            request, 
            f'Approved {updated} report(s).',
            messages.SUCCESS
        )
    approve_selected_reports.short_description = "Approve selected reports"
    
    def reject_selected_reports(self, request, queryset):
        """Admin action to reject selected reports"""
        updated = queryset.update(
            status='rejected', 
            reviewed_by=request.user, 
            reviewed_at=timezone.now()
        )
        self.message_user(
            request, 
            f'Rejected {updated} report(s).',
            messages.WARNING
        )
    reject_selected_reports.short_description = "Reject selected reports"
    
    def get_readonly_fields(self, request, obj=None):
        """Make certain fields read-only for non-superusers"""
        readonly_fields = list(self.readonly_fields)
        if not request.user.is_superuser:
            readonly_fields.extend(['reviewed_by', 'reviewed_at'])
        return readonly_fields
    
    def get_queryset(self, request):
        """Optimize queryset for admin display"""
        queryset = super().get_queryset(request)
        queryset = queryset.select_related(
            'event_assignment',
            'event_assignment__event',
            'event_assignment__team_member',
            'event_assignment__team_member__user',
            'reviewed_by'
        )
        return queryset