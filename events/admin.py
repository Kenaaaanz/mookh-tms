from django.contrib import admin
from .models import Event, EventAssignment

class EventAssignmentInline(admin.TabularInline):
    model = EventAssignment
    extra = 1

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'start_date', 'end_date', 'status']
    list_filter = ['status', 'start_date']
    search_fields = ['name', 'location']
    inlines = [EventAssignmentInline]

@admin.register(EventAssignment)
class EventAssignmentAdmin(admin.ModelAdmin):
    list_display = ['event', 'team_member', 'is_team_lead', 'assigned_at']
    list_filter = ['is_team_lead', 'assigned_at']
    search_fields = ['event__name', 'team_member__user__username']