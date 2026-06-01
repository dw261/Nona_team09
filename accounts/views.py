import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode as build_querystring
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import LoginForm, SignupForm
from .models import Profile
from .sms import normalize_phone_number, send_phone_verification, verify_phone_code


def get_or_create_profile(user):
    profile, _ = Profile.objects.get_or_create(
        user=user,
        defaults={
            'phone_number': user.username,
            'nickname': user.username,
        },
    )
    return profile


def welcome(request):
    if request.user.is_authenticated:
        return redirect('posts:group_list')
    return render(request, 'accounts/welcome.html')


def phone_start(request):
    if request.user.is_authenticated:
        return redirect('posts:group_list')

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number', '').strip()
        try:
            verification = send_phone_verification(phone_number)
        except (ImproperlyConfigured, ValidationError, RuntimeError) as error:
            message = error.messages[0] if isinstance(error, ValidationError) else str(error)
            return render(request, 'accounts/phone.html', {
                'phone_number': phone_number,
                'error': message,
            }, status=400)

        request.session['pending_phone_number'] = verification.phone_number
        return redirect('accounts:code')

    return render(request, 'accounts/phone.html')


def code(request):
    if request.user.is_authenticated:
        return redirect('posts:group_list')

    phone_number = request.session.get('pending_phone_number')
    if not phone_number:
        return redirect('accounts:phone')

    if request.method == 'POST':
        code_value = request.POST.get('code', '')
        try:
            verify_phone_code(phone_number, code_value)
        except ValidationError as error:
            return render(request, 'accounts/code.html', {
                'phone_number': phone_number,
                'error': error.messages[0],
            }, status=400)

        request.session['verified_phone_number'] = phone_number
        return redirect(f"{reverse('accounts:signup')}?{build_querystring({'phone_number': phone_number})}")

    return render(request, 'accounts/code.html', {'phone_number': phone_number})


@require_POST
def send_code_api(request):
    try:
        payload = json.loads(request.body.decode('utf-8')) if request.body else request.POST
        verification = send_phone_verification(payload.get('phone_number', ''))
    except (ImproperlyConfigured, ValidationError, RuntimeError, json.JSONDecodeError) as error:
        if isinstance(error, ValidationError):
            message = error.messages[0]
        elif isinstance(error, json.JSONDecodeError):
            message = '\uc694\uccad \ud615\uc2dd\uc774 \uc62c\ubc14\ub974\uc9c0 \uc54a\uc2b5\ub2c8\ub2e4.'
        else:
            message = str(error)
        return JsonResponse({'error': message}, status=400)

    request.session['pending_phone_number'] = verification.phone_number
    return JsonResponse({'status': 'sent', 'phone_number': verification.phone_number})


@require_POST
def verify_code_api(request):
    try:
        payload = json.loads(request.body.decode('utf-8')) if request.body else request.POST
        phone_number = payload.get('phone_number') or request.session.get('pending_phone_number', '')
        verification = verify_phone_code(phone_number, payload.get('code', ''))
    except (ValidationError, json.JSONDecodeError) as error:
        message = error.messages[0] if isinstance(error, ValidationError) else '\uc694\uccad \ud615\uc2dd\uc774 \uc62c\ubc14\ub974\uc9c0 \uc54a\uc2b5\ub2c8\ub2e4.'
        return JsonResponse({'error': message}, status=400)

    request.session['verified_phone_number'] = verification.phone_number
    return JsonResponse({'status': 'verified', 'phone_number': verification.phone_number})


def signup(request):
    if request.user.is_authenticated:
        return redirect('posts:group_list')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        phone_number = normalize_phone_number(request.POST.get('phone_number', ''))
        verified_phone_number = request.session.get('verified_phone_number')
        if phone_number != verified_phone_number:
            form.add_error('phone_number', '\uc804\ud654\ubc88\ud638 \uc778\uc99d\uc774 \ud544\uc694\ud569\ub2c8\ub2e4.')
        if form.is_valid():
            user = form.save()
            login(request, user)
            request.session.pop('pending_phone_number', None)
            request.session.pop('verified_phone_number', None)
            return redirect('accounts:location')
    else:
        initial_phone_number = request.GET.get('phone_number') or request.session.get('verified_phone_number', '')
        form = SignupForm(initial={'phone_number': initial_phone_number})

    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('posts:group_list')

    if request.method == 'POST':
        form = LoginForm(request, request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('posts:group_list')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('accounts:login')


@login_required
def mypage(request):
    get_or_create_profile(request.user)
    return render(request, 'accounts/mypage.html')


@login_required
def location(request):
    get_or_create_profile(request.user)
    return render(request, 'accounts/location.html')


@login_required
def complete(request):
    return render(request, 'accounts/complete.html')


@login_required
@require_POST
def verify_region(request):
    try:
        payload = json.loads(request.body.decode('utf-8'))
        latitude = float(payload.get('latitude'))
        longitude = float(payload.get('longitude'))
    except (TypeError, ValueError, json.JSONDecodeError):
        return JsonResponse({'error': '\uc704\ub3c4\uc640 \uacbd\ub3c4 \uac12\uc774 \uc62c\ubc14\ub974\uc9c0 \uc54a\uc2b5\ub2c8\ub2e4.'}, status=400)

    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return JsonResponse({'error': '\uc704\ub3c4 \ub610\ub294 \uacbd\ub3c4 \ubc94\uc704\uac00 \uc62c\ubc14\ub974\uc9c0 \uc54a\uc2b5\ub2c8\ub2e4.'}, status=400)

    if not settings.KAKAO_REST_API_KEY:
        return JsonResponse({'error': 'Kakao REST API \ud0a4\uac00 \uc124\uc815\ub418\uc9c0 \uc54a\uc558\uc2b5\ub2c8\ub2e4.'}, status=500)

    query = urlencode({'x': longitude, 'y': latitude})
    request_url = f'https://dapi.kakao.com/v2/local/geo/coord2address.json?{query}'
    kakao_request = Request(
        request_url,
        headers={'Authorization': f'KakaoAK {settings.KAKAO_REST_API_KEY}'},
    )

    try:
        with urlopen(kakao_request, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
    except HTTPError as error:
        return JsonResponse({'error': f'Kakao API \uc694\uccad \uc2e4\ud328: {error.code}'}, status=502)
    except URLError:
        return JsonResponse({'error': 'Kakao API\uc5d0 \uc5f0\uacb0\ud560 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4.'}, status=502)

    documents = data.get('documents') or []
    if not documents:
        return JsonResponse({'error': '\ud604\uc7ac \uc704\uce58\uc758 \uc8fc\uc18c\ub97c \ucc3e\uc744 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4.'}, status=404)

    address_info = documents[0].get('address') or {}
    road_address_info = documents[0].get('road_address') or {}
    address = road_address_info.get('address_name') or address_info.get('address_name') or ''
    region = address_info.get('region_3depth_name') or address_info.get('region_2depth_name') or ''

    profile = get_or_create_profile(request.user)
    profile.address = address
    profile.region = region
    profile.latitude = latitude
    profile.longitude = longitude
    profile.is_region_verified = True
    profile.region_verified_at = timezone.now()
    profile.save(
        update_fields=[
            'address',
            'region',
            'latitude',
            'longitude',
            'is_region_verified',
            'region_verified_at',
            'updated_at',
        ]
    )

    return JsonResponse({
        'verified': True,
        'address': address,
        'region': region,
    })
