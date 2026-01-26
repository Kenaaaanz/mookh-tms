from django.contrib import admin, messages
from .models import TeamMember

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'mpesa_number', 'daily_rate', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone', 'mpesa_number', 'id_number']
    readonly_fields = ['created_at']
    actions = ['verify_selected_members', 'unverify_selected_members']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'phone', 'id_number', 'address')
        }),
        ('Payment Information', {
            'fields': ('daily_rate', 'mpesa_number', 'mpesa_name')
        }),
        ('Verification', {
            'fields': ('is_verified', 'created_at')
        }),
    )
    
    def verify_selected_members(self, request, queryset):
        """Admin action to verify selected team members"""
        updated = queryset.update(is_verified=True)
        self.message_user(
            request, 
            f'Successfully verified {updated} team member(s).',
            messages.SUCCESS
        )
    verify_selected_members.short_description = "Verify selected team members"
    
    def unverify_selected_members(self, request, queryset):
        """Admin action to unverify selected team members"""
        updated = queryset.update(is_verified=False)
        self.message_user(
            request, 
            f'Successfully unverified {updated} team member(s).',
            messages.WARNING
        )
    unverify_selected_members.short_description = "Unverify selected team members"
    
    def get_readonly_fields(self, request, obj=None):
        """Make certain fields read-only for non-superusers"""
        if not request.user.is_superuser:
            return self.readonly_fields + ('is_verified',)
        return self.readonly_fields
    
    def get_queryset(self, request):
        """Optimize queryset for admin display"""
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('user')
        return queryset