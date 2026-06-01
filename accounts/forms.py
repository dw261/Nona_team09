import re

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from .models import Profile


class SignupForm(forms.Form):
    phone_number = forms.CharField(max_length=20, label='\uc804\ud654\ubc88\ud638')
    nickname = forms.CharField(max_length=50, label='\ub2c9\ub124\uc784')
    password1 = forms.CharField(widget=forms.PasswordInput, label='\ube44\ubc00\ubc88\ud638')
    password2 = forms.CharField(widget=forms.PasswordInput, label='\ube44\ubc00\ubc88\ud638 \ud655\uc778')

    def clean_phone_number(self):
        phone_number = re.sub(r'[\s-]', '', self.cleaned_data['phone_number'].strip())
        if not phone_number.isdigit() or len(phone_number) not in (10, 11):
            raise forms.ValidationError('\uc804\ud654\ubc88\ud638 \ud615\uc2dd\uc774 \uc62c\ubc14\ub974\uc9c0 \uc54a\uc2b5\ub2c8\ub2e4.')
        if User.objects.filter(username=phone_number).exists():
            raise forms.ValidationError('\uc774\ubbf8 \uac00\uc785\ub41c \uc804\ud654\ubc88\ud638\uc785\ub2c8\ub2e4.')
        if Profile.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError('\uc774\ubbf8 \uac00\uc785\ub41c \uc804\ud654\ubc88\ud638\uc785\ub2c8\ub2e4.')
        return phone_number

    def clean_nickname(self):
        nickname = self.cleaned_data['nickname'].strip()
        if len(nickname) < 2:
            raise forms.ValidationError('\ub2c9\ub124\uc784\uc740 2\uc790 \uc774\uc0c1 \uc785\ub825\ud574 \uc8fc\uc138\uc694.')
        return nickname

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            self.add_error('password2', '\ube44\ubc00\ubc88\ud638\uac00 \uc77c\uce58\ud558\uc9c0 \uc54a\uc2b5\ub2c8\ub2e4.')

        if password1:
            validate_password(password1)

        return cleaned_data

    def save(self):
        phone_number = self.cleaned_data['phone_number']
        nickname = self.cleaned_data['nickname']
        password = self.cleaned_data['password1']

        user = User.objects.create_user(
            username=phone_number,
            password=password,
        )
        profile, created = Profile.objects.get_or_create(
            user=user,
            defaults={
                'phone_number': phone_number,
                'nickname': nickname,
            },
        )
        if not created:
            profile.phone_number = phone_number
            profile.nickname = nickname
            profile.save(update_fields=['phone_number', 'nickname', 'updated_at'])
        return user


class LoginForm(forms.Form):
    phone_number = forms.CharField(max_length=20, label='\uc804\ud654\ubc88\ud638')
    password = forms.CharField(widget=forms.PasswordInput, label='\ube44\ubc00\ubc88\ud638')

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.user = None

    def clean(self):
        cleaned_data = super().clean()
        phone_number = cleaned_data.get('phone_number')
        password = cleaned_data.get('password')

        if phone_number and password:
            phone_number = re.sub(r'[\s-]', '', phone_number.strip())
            cleaned_data['phone_number'] = phone_number
            self.user = authenticate(
                self.request,
                username=phone_number,
                password=password,
            )
            if self.user is None:
                raise forms.ValidationError('\uc804\ud654\ubc88\ud638 \ub610\ub294 \ube44\ubc00\ubc88\ud638\uac00 \uc62c\ubc14\ub974\uc9c0 \uc54a\uc2b5\ub2c8\ub2e4.')

        return cleaned_data

    def get_user(self):
        return self.user
