from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from .models import TeamMember

class TeamMemberForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    
    # M-Pesa phone validation (Kenya format)
    phone = forms.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+254712345678'. Up to 15 digits allowed."
            )
        ]
    )
    
    mpesa_number = forms.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?254\d{9}$|^0\d{9}$',
                message="M-Pesa number must be in format: 0712345678 or +254712345678"
            )
        ],
        help_text="Enter your M-Pesa registered phone number"
    )
    
    class Meta:
        model = TeamMember
        fields = ['first_name', 'last_name', 'email', 'phone', 'id_number', 
                 'address', 'mpesa_number', 'mpesa_name']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
    
    def save(self, commit=True):
        team_member = super().save(commit=False)
        if team_member.user:
            team_member.user.first_name = self.cleaned_data['first_name']
            team_member.user.last_name = self.cleaned_data['last_name']
            team_member.user.email = self.cleaned_data['email']
            team_member.user.save()
        if commit:
            team_member.save()
        return team_member


class TeamMemberRegistrationForm(UserCreationForm):
    # Personal Details
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter your first name'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter your last name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Enter your email address'}))
    
    # Contact Details
    phone = forms.CharField(
        max_length=15,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^\+?254\d{9}$|^0\d{9}$',
                message="Phone number must be in format: 0712345678 or +254712345678"
            )
        ],
        widget=forms.TextInput(attrs={'placeholder': '0712345678 or +254712345678'})
    )
    
    # M-Pesa Details (for payments)
    mpesa_number = forms.CharField(
        max_length=15,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^\+?254\d{9}$|^0\d{9}$',
                message="M-Pesa number must be in format: 0712345678 or +254712345678"
            )
        ],
        help_text="This is where your payments will be sent",
        widget=forms.TextInput(attrs={'placeholder': 'M-Pesa registered number'})
    )
    
    mpesa_name = forms.CharField(
        max_length=100,
        required=False,
        help_text="Name as registered in M-Pesa (optional)",
        widget=forms.TextInput(attrs={'placeholder': 'Your name in M-Pesa'})
    )
    
    # Personal Information
    id_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'National ID number (optional)'})
    )
    
    address = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter your physical address'})
    )
    
    # Terms and Conditions
    terms_accepted = forms.BooleanField(
        required=True,
        label="I agree to the terms and conditions"
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 
                 'mpesa_number', 'mpesa_name', 'id_number', 'address',
                 'password1', 'password2', 'terms_accepted']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Choose a username'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Create a password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm password'})
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Format phone number consistently
        if phone.startswith('0'):
            phone = '+254' + phone[1:]
        elif not phone.startswith('+254'):
            phone = '+254' + phone
        
        if TeamMember.objects.filter(phone=phone).exists():
            raise forms.ValidationError("This phone number is already registered.")
        return phone
    
    def clean_mpesa_number(self):
        mpesa_number = self.cleaned_data.get('mpesa_number')
        # Format M-Pesa number consistently
        if mpesa_number.startswith('0'):
            mpesa_number = '+254' + mpesa_number[1:]
        elif not mpesa_number.startswith('+254'):
            mpesa_number = '+254' + mpesa_number
        
        if TeamMember.objects.filter(mpesa_number=mpesa_number).exists():
            raise forms.ValidationError("This M-Pesa number is already registered.")
        return mpesa_number
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            
            # Create TeamMember profile with M-Pesa fields
            team_member = TeamMember.objects.create(
                user=user,
                phone=self.cleaned_data['phone'],
                mpesa_number=self.cleaned_data['mpesa_number'],
                mpesa_name=self.cleaned_data.get('mpesa_name', ''),
                id_number=self.cleaned_data.get('id_number', ''),
                address=self.cleaned_data['address'],
                daily_rate=0.00,  # Default daily rate, will be set per invoice
                is_verified=False  # Admin needs to verify
            )
        
        return user