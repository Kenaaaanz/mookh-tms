from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from teams import views as team_views
from events import views as event_views
from invoices import views as invoice_views
from django.conf import settings
from django.conf.urls.static import static

# Custom admin site header
admin.site.site_header = "Mookh Ticket System Administration"
admin.site.site_title = "Mookh Admin"
admin.site.index_title = "Welcome to Mookh Team Management System"


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', team_views.dashboard, name='dashboard'),
    path('register/', team_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', team_views.custom_logout, name='logout'),    
    # Profile
    path('profile/', team_views.profile_view, name='profile'),
    
    # Events
    path('events/', event_views.event_list, name='event_list'),
    path('events/my/', event_views.my_events, name='my_events'),
    path('events/create/', event_views.create_event, name='create_event'),
    path('events/<int:event_id>/', event_views.event_detail, name='event_detail'),
    path('events/<int:event_id>/assign/', event_views.assign_team_members, name='assign_team_members'),
    
    # Invoices
    path('invoices/my/', invoice_views.my_invoices, name='my_invoices'),
    path('invoices/create/<int:assignment_id>/', invoice_views.create_invoice, name='create_invoice'),
    path('invoices/<int:invoice_id>/download/', invoice_views.download_invoice, name='download_invoice'),
    path('invoices/<int:invoice_id>/verify/', invoice_views.verify_invoice, name='verify_invoice'),
    
    # Reports
    path('reports/my/', invoice_views.my_reports, name='my_reports'),
    path('reports/create/<int:assignment_id>/', invoice_views.create_report, name='create_report'),
    path('reports/<int:report_id>/download/', invoice_views.download_report, name='download_report'),
    path('reports/<int:report_id>/review/', invoice_views.review_report, name='review_report'),

    path('invoices/<int:invoice_id>/submit/', invoice_views.submit_invoice, name='submit_invoice'),
    path('invoices/<int:invoice_id>/', invoice_views.invoice_detail, name='invoice_detail'),

    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)