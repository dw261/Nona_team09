import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import LoginForm, SignupForm
from .models import Profile


def get_or_create_profile(user):
    profile, _ = Profile.objects.get_or_create(
        user=user,
        defaults={
            'phone_number': user.username,
            'nickname': user.username,
        },
    )
    return profile


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('posts:group_list')
    else:
        form = SignupForm()

    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
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
    return redirect('posts:group_list')


@login_required
def mypage(request):
    get_or_create_profile(request.user)
    return render(request, 'accounts/mypage.html')


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
