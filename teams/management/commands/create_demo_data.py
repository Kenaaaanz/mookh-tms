from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from teams.models import TeamMember
from events.models import Event, EventAssignment
from invoices.models import Invoice, EventReport
from django.utils import timezone
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Create demo data for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating demo data...')
        
        # Create admin user if not exists
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@mookh.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write('Created admin user')
        
        # Create regular user if not exists
        regular_user, created = User.objects.get_or_create(
            username='user',
            defaults={
                'email': 'user@mookh.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'is_staff': False
            }
        )
        if created:
            regular_user.set_password('user123')
            regular_user.save()
            self.stdout.write('Created regular user')
        
        # Create team members
        team_members_data = [
            {
                'user': regular_user,
                'phone': '+1234567890',
                'address': '123 Main St, City',
                'bank_name': 'Demo Bank',
                'account_number': '1234567890',
                'ifsc_code': 'DEMO123456',
                'hourly_rate': 25.00,
                'is_verified': True
            },
            {
                'user': User.objects.create_user(
                    username='jane.smith',
                    email='jane@mookh.com',
                    password='demo123',
                    first_name='Jane',
                    last_name='Smith'
                ),
                'phone': '+1987654321',
                'address': '456 Oak Ave, Town',
                'bank_name': 'Sample Bank',
                'account_number': '0987654321',
                'ifsc_code': 'SAMPLE09876',
                'hourly_rate': 30.00,
                'is_verified': True
            },
            {
                'user': User.objects.create_user(
                    username='bob.johnson',
                    email='bob@mookh.com',
                    password='demo123',
                    first_name='Bob',
                    last_name='Johnson'
                ),
                'phone': '+1122334455',
                'address': '789 Pine Rd, Village',
                'bank_name': 'Test Bank',
                'account_number': '1122334455',
                'ifsc_code': 'TEST112233',
                'hourly_rate': 22.50,
                'is_verified': False
            }
        ]
        
        team_members = []
        for data in team_members_data:
            team_member, created = TeamMember.objects.get_or_create(
                user=data['user'],
                defaults=data
            )
            if created:
                team_members.append(team_member)
                self.stdout.write(f'Created team member: {team_member.user.get_full_name()}')
        
        # Create events
        events_data = [
            {
                'name': 'Tech Conference 2024',
                'description': 'Annual technology conference with keynote speakers and workshops',
                'location': 'Convention Center, Downtown',
                'start_date': timezone.now() + timedelta(days=30),
                'end_date': timezone.now() + timedelta(days=32),
                'status': 'upcoming',
                'created_by': admin_user
            },
            {
                'name': 'Music Festival Tickets',
                'description': 'Weekend music festival ticket validation and assistance',
                'location': 'Central Park',
                'start_date': timezone.now() + timedelta(days=15),
                'end_date': timezone.now() + timedelta(days=17),
                'status': 'upcoming',
                'created_by': admin_user
            },
            {
                'name': 'Sports Championship',
                'description': 'National sports championship event ticket management',
                'location': 'Stadium Arena',
                'start_date': timezone.now() - timedelta(days=10),
                'end_date': timezone.now() - timedelta(days=8),
                'status': 'completed',
                'created_by': admin_user
            },
            {
                'name': 'Business Expo',
                'description': 'Business networking and exhibition event',
                'location': 'Exhibition Hall',
                'start_date': timezone.now() + timedelta(days=45),
                'end_date': timezone.now() + timedelta(days=47),
                'status': 'upcoming',
                'created_by': admin_user
            }
        ]
        
        events = []
        for data in events_data:
            event, created = Event.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            if created:
                events.append(event)
                self.stdout.write(f'Created event: {event.name}')
        
        # Assign team members to events
        assignments_data = [
            (events[0], [team_members[0], team_members[1]], team_members[0]),
            (events[1], [team_members[0], team_members[2]], team_members[2]),
            (events[2], [team_members[0], team_members[1], team_members[2]], team_members[1]),
            (events[3], [team_members[1]], team_members[1])
        ]
        
        for event, assigned_members, team_lead in assignments_data:
            for team_member in assigned_members:
                assignment, created = EventAssignment.objects.get_or_create(
                    event=event,
                    team_member=team_member,
                    defaults={'is_team_lead': team_member == team_lead}
                )
                if created:
                    self.stdout.write(f'Assigned {team_member.user.get_full_name()} to {event.name}')
        
        # Create invoices for completed event
        completed_event = events[2]
        for assignment in completed_event.assignments.all():
            invoice, created = Invoice.objects.get_or_create(
                event_assignment=assignment,
                defaults={
                    'total_hours': random.randint(8, 40),
                    'hourly_rate': assignment.team_member.hourly_rate,
                    'due_date': timezone.now() + timedelta(days=30),
                    'status': random.choice(['submitted', 'verified', 'paid']),
                    'is_verified': True,
                    'verified_by': admin_user,
                    'verified_at': timezone.now() - timedelta(days=5)
                }
            )
            if created:
                invoice.save()
                self.stdout.write(f'Created invoice for {assignment.team_member.user.get_full_name()}')
        
        # Create reports for completed event
        for assignment in completed_event.assignments.all():
            report, created = EventReport.objects.get_or_create(
                event_assignment=assignment,
                defaults={
                    'report_content': f'Work summary for {assignment.event.name}',
                    'attendance_hours': random.randint(8, 40),
                    'work_summary': f'Successfully managed ticket validation for {assignment.event.name}. Handled customer queries and ensured smooth entry process.',
                    'challenges_faced': 'High volume of attendees during peak hours.',
                    'suggestions': 'Implement additional entry gates for faster processing.',
                    'status': random.choice(['approved', 'pending']),
                    'reviewed_by': admin_user if random.choice([True, False]) else None,
                    'reviewed_at': timezone.now() - timedelta(days=3) if random.choice([True, False]) else None
                }
            )
            if created:
                self.stdout.write(f'Created report for {assignment.team_member.user.get_full_name()}')
        
        self.stdout.write(self.style.SUCCESS('Demo data created successfully!'))
        self.stdout.write('\nDemo Accounts:')
        self.stdout.write('  Admin: admin / admin123')
        self.stdout.write('  User: user / user123')
        self.stdout.write('  Jane: jane.smith / demo123')
        self.stdout.write('  Bob: bob.johnson / demo123')