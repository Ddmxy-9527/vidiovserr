from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from django.http import JsonResponse
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
import random
from .models import EmailVerificationCode

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('video_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def send_verification_code(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'msg': 'Invalid request'}, status=400)
    email = request.POST.get('email', '').strip()
    if not email:
        return JsonResponse({'ok': False, 'msg': 'Please enter email'}, status=400)
    code = f'{random.randint(100000, 999999)}'
    expires = timezone.now() + timedelta(minutes=10)
    EmailVerificationCode.objects.create(email=email, code=code, expires_at=expires)
    try:
        from django.conf import settings
        send_mail(
            'Your verification code',
            f'Your code is {code}. It expires in 10 minutes.',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        return JsonResponse({'ok': True, 'msg': 'Verification code sent'})
    except Exception as e:
        import traceback, sys
        traceback.print_exc()  # 打印完整堆栈到控制台
        return JsonResponse({'ok': False, 'msg': f'Failed to send email: {e}'}, status=500)
