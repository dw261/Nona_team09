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
def verify_region(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST 요청만 가능합니다.'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8'))
        latitude = float(payload.get('latitude'))
        longitude = float(payload.get('longitude'))
    except (TypeError, ValueError, json.JSONDecodeError):
        return JsonResponse({'error': '위도와 경도 값이 올바르지 않습니다.'}, status=400)

    if not settings.KAKAO_REST_API_KEY:
        return JsonResponse({'error': 'Kakao REST API 키가 설정되지 않았습니다.'}, status=500)

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
        return JsonResponse({'error': f'Kakao API 요청 실패: {error.code}'}, status=502)
    except URLError:
        return JsonResponse({'error': 'Kakao API에 연결할 수 없습니다.'}, status=502)

    documents = data.get('documents') or []
    if not documents:
        return JsonResponse({'error': '현재 위치의 주소를 찾을 수 없습니다.'}, status=404)

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
