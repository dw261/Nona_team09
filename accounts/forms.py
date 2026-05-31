from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from .models import Profile


class SignupForm(forms.Form):
    phone_number = forms.CharField(max_length=20, label='전화번호')
    nickname = forms.CharField(max_length=50, label='닉네임')
    password1 = forms.CharField(widget=forms.PasswordInput, label='비밀번호')
    password2 = forms.CharField(widget=forms.PasswordInput, label='비밀번호 확인')

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number'].strip()
        if User.objects.filter(username=phone_number).exists():
            raise forms.ValidationError('이미 가입된 전화번호입니다.')
        if Profile.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError('이미 가입된 전화번호입니다.')
        return phone_number

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            self.add_error('password2', '비밀번호가 일치하지 않습니다.')

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
        Profile.objects.create(
            user=user,
            phone_number=phone_number,
            nickname=nickname,
        )
        return user


class LoginForm(forms.Form):
    phone_number = forms.CharField(max_length=20, label='전화번호')
    password = forms.CharField(widget=forms.PasswordInput, label='비밀번호')

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.user = None

    def clean(self):
        cleaned_data = super().clean()
        phone_number = cleaned_data.get('phone_number')
        password = cleaned_data.get('password')

        if phone_number and password:
            self.user = authenticate(
                self.request,
                username=phone_number,
                password=password,
            )
            if self.user is None:
                raise forms.ValidationError('전화번호 또는 비밀번호가 올바르지 않습니다.')

        return cleaned_data

    def get_user(self):
        return self.user
