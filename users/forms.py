from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms
from django.utils import timezone
from .models import EmailVerificationCode

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    verification_code = forms.CharField(label='Verification Code')
    class Meta:
        model = User
        fields = ('email', 'verification_code')
        labels = {
            'email': 'Email',
            'verification_code': 'Verification Code',
        }
    def clean(self):
        cleaned = super().clean()
        email = cleaned.get('email')
        code = cleaned.get('verification_code')
        if email and code:
            rec = EmailVerificationCode.objects.filter(email=email).order_by('-created_at').first()
            if not rec or rec.code != code or not rec.is_valid():
                raise forms.ValidationError('Invalid or expired verification code')
        return cleaned
