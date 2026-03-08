# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class TeamMember(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='team_member')
    phone = models.CharField(max_length=15, unique=True)  # M-Pesa phone number
    id_number = models.CharField(max_length=20, blank=True, null=True)  # National ID
    address = models.TextField()
    shift_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    mpesa_number = models.CharField(max_length=15, default="")  # M-Pesa phone for payments
    mpesa_name = models.CharField(max_length=100, blank=True)  # Name as registered in M-Pesa
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.mpesa_number}"