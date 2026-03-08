from django.contrib import admin, messages
from django.utils import timezone
from .models import Invoice, EventReport

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'event_assignment', 'number_of_days', 'shift_rate', 
                   'total_amount', 'payment_method', 'status', 'is_verified', 'formatted_invoice_date']
    list_filter = ['status', 'is_verified', 'payment_method', 'invoice_date']
    search_fields = ['mpesa_transaction_id', 'mpesa_confirmation_code',
                    'event_assignment__event__name',
                    'event_assignment__team_member__user__username']
    readonly_fields = ['total_amount', 'created_at', 'invoice_date', 'formatted_invoice_date']  # Added invoice_date as readonly
    actions = ['mark_as_paid', 'mark_as_verified']
    
    fieldsets = (
        ('Invoice Details', {
            'fields': ('event_assignment', 'number_of_days', 'shift_rate', 'total_amount')
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
    
    def formatted_invoice_date(self, obj):
        """Display invoice date in a readable format"""
        return obj.invoice_date.strftime("%B %d, %Y")
    formatted_invoice_date.short_description = 'Invoice Date'
    
    def mark_as_paid(self, request, queryset):
        """Admin action to mark selected invoices as paid"""
        updated = queryset.update(
            status='paid', 
            paid_at=timezone.now()
        )
        self.message_user(
            request, 
            f'Marked {updated} invoice(s) as paid.',
            messages.SUCCESS
        )
    mark_as_paid.short_description = "Mark selected invoices as paid"
    
    def mark_as_verified(self, request, queryset):
        """Admin action to mark selected invoices as verified"""
        updated = queryset.update(
            is_verified=True, 
            verified_by=request.user, 
            verified_at=timezone.now(),
            status='verified'
        )
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
            readonly_fields.extend(['shift_rate', 'number_of_days', 'event_assignment'])
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
    
    def save_model(self, request, obj, form, change):
        """Override save to handle verified_by"""
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(EventReport)
class EventReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'event_assignment', 'status', 'attendance_hours', 'submitted_at', 'reviewed_by', 'formatted_status']
    list_filter = ['status', 'submitted_at']
    search_fields = ['event_assignment__event__name', 
                    'event_assignment__team_member__user__username',
                    'work_summary']
    readonly_fields = ['submitted_at', 'formatted_status']
    actions = ['approve_selected_reports', 'reject_selected_reports']
    fieldsets = (
        ('Report Details', {
            'fields': ('event_assignment', 'attendance_hours', 'work_summary', 'formatted_status')
        }),
        ('Additional Information', {
            'fields': ('challenges_faced', 'suggestions', 'submitted_at'),
            'classes': ('wide',)
        }),
        ('Review Information', {
            'fields': ('status', 'review_notes', 'reviewed_by', 'reviewed_at'),
            'classes': ('wide',)
        }),
    )
    
    def formatted_status(self, obj):
        """Display formatted status with icon"""
        status_icons = {
            'pending': '🕒',
            'approved': '✅',
            'rejected': '❌'
        }
        return f"{status_icons.get(obj.status, '')} {obj.get_status_display()}"
    formatted_status.short_description = 'Status'
    
    def get_readonly_fields(self, request, obj=None):
        """Make fields readonly based on object state"""
        readonly_fields = list(self.readonly_fields)
        
        if obj and obj.status in ['approved', 'rejected']:
            readonly_fields.extend(['status', 'review_notes', 'event_assignment', 'attendance_hours', 'work_summary'])
        
        if not request.user.is_superuser:
            readonly_fields.extend(['reviewed_by', 'reviewed_at'])
        
        return readonly_fields
    
    def save_model(self, request, obj, form, change):
        """Override save to handle review actions"""
        if '_approve' in request.POST:
            obj.status = 'approved'
            obj.reviewed_by = request.user
            obj.reviewed_at = timezone.now()
        elif '_reject' in request.POST:
            obj.status = 'rejected'
            obj.reviewed_by = request.user
            obj.reviewed_at = timezone.now()
        super().save_model(request, obj, form, change)
    
    def response_change(self, request, obj):
        """Handle redirect after save"""
        if '_approve' in request.POST or '_reject' in request.POST:
            self.message_user(request, f"Report #{obj.id} has been {obj.get_status_display().lower()}.")
            return redirect(f'/admin/invoices/eventreport/{obj.id}/change/#review-information-tab')
        return super().response_change(request, obj)