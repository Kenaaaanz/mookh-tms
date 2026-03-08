from django.contrib import admin
from django.utils.html import format_html
from .models import Event, EventAssignment

class EventAssignmentInline(admin.TabularInline):
    model = EventAssignment
    extra = 1
    fields = ['team_member', 'is_team_lead', 'assigned_at']
    readonly_fields = ['assigned_at']
    autocomplete_fields = ['team_member']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('team_member', 'team_member__user')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'start_date', 'end_date', 'status', 'team_count', 'created_at']
    list_filter = ['status', 'start_date', 'end_date']
    search_fields = ['name', 'location', 'description']
    readonly_fields = ['created_at', 'created_by']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Event Information', {
            'fields': ('name', 'description', 'location')
        }),
        ('Date & Time', {
            'fields': ('start_date', 'end_date', 'status')
        }),
        ('System Information', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [EventAssignmentInline]
    
    def team_count(self, obj):
        count = obj.assignments.count()
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            'success' if count > 0 else 'secondary',
            f'{count} member{"s" if count != 1 else ""}'
        )
    team_count.short_description = 'Team'
    team_count.admin_order_field = 'assignments__count'
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('assignments', 'assignments__team_member')
    
    class Media:
        css = {
            'all': ('css/admin-tabs.css',)
        }
        js = ('js/admin-tabs.js',)


@admin.register(EventAssignment)
class EventAssignmentAdmin(admin.ModelAdmin):
    list_display = ['event', 'team_member', 'is_team_lead', 'assigned_at']
    list_filter = ['is_team_lead', 'assigned_at']
    search_fields = ['event__name', 'team_member__user__username']
    autocomplete_fields = ['event', 'team_member']
    
    fieldsets = (
        ('Assignment Details', {
            'fields': ('event', 'team_member')
        }),
        ('Role', {
            'fields': ('is_team_lead', 'assigned_at')
        }),
    )
    
    readonly_fields = ['assigned_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('event', 'team_member', 'team_member__user')