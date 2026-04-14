from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.auth.models import User
from .models import TeamMember


class UserAdmin(admin.ModelAdmin):
    search_fields = ['username', 'email', 'first_name', 'last_name']
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']


# Re-register UserAdmin to add search capability
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['get_user_display', 'phone', 'mpesa_number', 'shift_rate', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone', 'mpesa_number', 'id_number']
    readonly_fields = ['created_at']
    list_editable = ['is_verified']
    actions = ['verify_selected_members', 'unverify_selected_members']
    autocomplete_fields = ['user']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'phone', 'id_number', 'address')
        }),
        ('Payment Information', {
            'fields': ('shift_rate', 'mpesa_number', 'mpesa_name'),
            'classes': ('wide',)
        }),
        ('Verification', {
            'fields': ('is_verified', 'created_at'),
            'classes': ('wide',)
        }),
    )
    
    def get_user_display(self, obj):
        if obj.user:
            return f"{obj.user.get_full_name()} ({obj.user.username})"
        return "-"
    get_user_display.short_description = 'User'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')
    
    def verify_selected_members(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'Successfully verified {updated} team member(s).')
    verify_selected_members.short_description = "Verify selected team members"
    
    def unverify_selected_members(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'Successfully unverified {updated} team member(s).')
    unverify_selected_members.short_description = "Unverify selected team members"
    
    class Media:
        css = {
            'all': ('css/admin-tabs.css',)
        }
        js = ('js/admin-tabs.js',)