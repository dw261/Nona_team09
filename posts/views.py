from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from django.http import JsonResponse
from posts.models import *
from posts.forms import GroupPostForm, SharingPostForm
from django.db.models import Case, When, IntegerField, Q
from django.utils.dateparse import parse_datetime
import json

# ================================================
# 공구
# ================================================
def group_list(request):
    current_sort = request.GET.get('sort', 'latest')  # 기본값은 최신순

    # 상태 우선순위 정렬 (모집중 → 마감 → 완료)
    status_order = Case(
        When(status='recruiting', then=0),
        When(status='closed', then=1),
        When(status='done', then=2),
        default=3,
        output_field=IntegerField(),
    )
    
    sort_options = {
        'deadline': 'deadline',  # 마감임박순
        'latest': '-created_at', # 최신순
        'oldest': 'created_at',  # 오래된순
        'price_low': 'price_per',    # 가격 낮은순
        'price_high': '-price_per',  # 가격 높은순
    }
    
    secondary_sort = sort_options.get(current_sort, '-created_at')

    queryset = (
        groupsPost.objects
        .select_related('host', 'category')
        .prefetch_related('groupImages')
        .annotate(status_order=status_order)
        .order_by('status_order', secondary_sort)
    )

    # 검색
    query = request.GET.get('q', '')
    if query:
        keywords = [kw.strip() for kw in query.split(',') if kw.strip()]
        
        query_filter = Q()
        for kw in keywords:
            # 각 키워드가 제목(title)에 포함되어 있는가? (OR 조건 축적)
            query_filter |= Q(title__icontains=kw)
            
        queryset = queryset.filter(query_filter)
    
    # 카테고리 필터
    category_id = request.GET.get('category', '')
    if category_id:
        queryset = queryset.filter(category_id=category_id)
 
    # 찜 목록
    wished_ids = []
    if request.user.is_authenticated:
        wished_ids = list(
            request.user.wishes.filter(group__isnull=False).values_list('group_id', flat=True)
        )

    context = {
        'groups': queryset,
        'categories': Category.objects.all(),
        'current_sort': current_sort,
        'query': query,
        'wished_ids': wished_ids,
    }
    return render(request, 'posts/group_list.html', context)

# 공구 개설 페이지
@login_required
def group_create(request):
    if request.method == 'POST':
        form = GroupPostForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.host = request.user

            date_str = request.POST.get('deadline_date')
            time_str = request.POST.get('deadline_time')
            if date_str and time_str:
                # 'YYYY-MM-DDTHH:MM:SS' 포맷 문자열 생성 후 파싱
                group.deadline = parse_datetime(f"{date_str}T{time_str}:00")

            group.save()

            images = request.FILES.getlist('images')
            for order, image in enumerate(images):
                groupImage.objects.create(group=group, photo=image, order=order)

            return redirect('posts:group_detail', group_id=group.pk)
        else:
            print("❌ 나눔 개설 폼 검증 실패:", form.errors)
    else:
        form = GroupPostForm()

    return render(request, 'posts/group_create.html', {'form': form, 'categories': Category.objects.all()})

# 공구 상세 페이지
def group_detail(request, group_id):
    group = get_object_or_404(
        groupsPost.objects.select_related('host', 'category').prefetch_related('groupImages', 'groupsParticipants__user'), 
        pk=group_id
    )
    is_participated = False

    if request.user.is_authenticated:
        is_participated = groupsParticipant.objects.filter(user=request.user, group=group).exists()

    context = {
        'group': group,
        'is_participated': is_participated,
        'participation_count': group.groupsParticipants.filter(
            status='approved'
        ).count(),
    }

    return render(request, 'posts/group_detail.html', context)

# 공구 수정 페이지
@login_required
def group_update(request, group_id):
    group = get_object_or_404( # 본인만 수정 가능
        groupsPost,
        pk=group_id,
        host=request.user,
    )

    if request.method == 'POST':
        group.category_id = request.POST.get('category')
        group.title       = request.POST.get('title')
        group.content     = request.POST.get('content')
        group.min_members = request.POST.get('min_members')
        group.price_per   = request.POST.get('price_per')
        group.location    = request.POST.get('location')
        group.deadline    = request.POST.get('deadline')
        group.link        = request.POST.get('link', '')
        group.save()

        # 이미지 추가
        images = request.FILES.getlist('images')
        current_order = group.images.count()  # 기존 이미지 개수만큼 order 시작
        for order, image in enumerate(images, start=current_order):
            groupImage.objects.create(group=group, photo=image, order=order)

        return redirect('posts:group_detail', pk=group.pk)
    
    context = {
        'group_id': group_id,
        'group': group,
        'categories': Category.objects.all(),
    }
    return render(request, 'posts/group_update.html', context)

# 공구 삭제 페이지
@login_required
@require_POST
def group_delete(request, group_id):
    group = get_object_or_404( # 본인만 삭제 가능
        groupsPost,
        pk=group_id,
        host=request.user,
    )
    group.delete()
    return redirect('posts:group_list')

# 공구 참여
@login_required
@require_POST
def group_participate(request, group_id):
    group = get_object_or_404(groupsPost, pk=group_id)
    if group.host == request.user:
        return JsonResponse({'error': '호스트는 참여할 수 없습니다.'}, status=400)
    participation, created = groupsParticipant.objects.get_or_create(
        group=group,
        user=request.user,
    )
    if not created:
        return JsonResponse({'error': '이미 참여 신청한 공구입니다.'}, status=400)
    
    # 참여 인원 업데이트
    group.current_members += 1
    group.save()

    return redirect('chat:room', pk=group_id)  # 채팅방으로 이동

# 공구 찜 토글
@login_required
@require_POST
def group_wish_toggle(request, group_id):
    group = get_object_or_404(groupsPost, pk=group_id)
    wish  = Wish.objects.filter(user=request.user, group=group)
    if wish.exists():
        wish.delete()
        wished = False
    else:
        Wish.objects.create(user=request.user, group=group)
        wished = True
    return JsonResponse({'wished': wished})

# ================================================
# 나눔
# ================================================
def shares_list(request):
    current_sort = request.GET.get('sort', 'latest')  # 기본값은 최신순

    status_order = Case(
        When(status='recruiting', then=0),
        When(status='closed', then=1),
        When(status='done', then=2),
        default=3,
        output_field=IntegerField(),
    )

    sort_options = {
        'deadline': 'deadline',  # 마감임박순
        'latest': '-created_at', # 최신순
        'oldest': 'created_at',  # 오래된순
    }
    secondary_sort = sort_options.get(current_sort, '-created_at')

    queryset = (
        sharingPost.objects
        .select_related('host', 'category')
        .prefetch_related('shareImage')
        .annotate(status_order=status_order)
        .order_by('status_order', secondary_sort)
    )

    # 검색
    query = request.GET.get('q', '')
    if query:
        keywords = [kw.strip() for kw in query.split(',') if kw.strip()]
        
        query_filter = Q()
        for kw in keywords:
            query_filter |= Q(title__icontains=kw)
            
        queryset = queryset.filter(query_filter)
    
    # 카테고리 필터
    category_id = request.GET.get('category', '')
    if category_id:
        queryset = queryset.filter(category_id=category_id)
 
    # 찜 목록
    wished_ids = []
    if request.user.is_authenticated:
        wished_ids = list(
            request.user.wishes.filter(sharing__isnull=False).values_list('sharing_id', flat=True)
        )

    context = {
        'shares': queryset,
        'query': query,
        'current_sort': current_sort, 
        'categories': Category.objects.all(),
        'wished_ids': wished_ids,
    }
    return render(request, 'posts/share_list.html', context)

# 나눔 개설 페이지
@login_required
def shares_create(request):
    if request.method == 'POST':
        form = SharingPostForm(request.POST)
        if form.is_valid():
            share = form.save(commit=False)
            share.host = request.user

            date_str = request.POST.get('deadline_date')
            time_str = request.POST.get('deadline_time')
            if date_str and time_str:
                share.deadline = parse_datetime(f"{date_str}T{time_str}:00")

            share.save()

            images = request.FILES.getlist('images')
            for order, image in enumerate(images):
                SharingImage.objects.create(sharing=share, photo=image, order=order)

            return redirect('posts:shares_detail', share_id=share.pk)
        else:
            print("❌ 나눔 개설 폼 검증 실패:", form.errors)
    else:
        form = SharingPostForm()

    return render(request, 'posts/share_create.html', {'form': form, 'categories': Category.objects.all()})

# 나눔 상세 페이지
def shares_detail(request, share_id):
    share = get_object_or_404(
        sharingPost.objects.select_related('host', 'category').prefetch_related('shareImage'), 
        pk=share_id
    )
    is_participated = False

    if request.user.is_authenticated:
        is_participated = SharingParticipant.objects.filter(user=request.user, sharing=share).exists()

    context = {
        'sharing': share,
        'is_participated': is_participated,
        'participation_count': SharingParticipant.objects.filter(sharing=share, status='approved').count(),
    }

    return render(request, 'posts/share_detail.html', context)

# 나눔 수정 페이지
@login_required
@require_http_methods(["PATCH"])
def shares_update(request, share_id):
    share = get_object_or_404( # 본인만 수정 가능
        sharingPost,
        pk=share_id,
        host=request.user,
    )

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': '올바르지 않은 데이터 형식입니다.'}, status=400)

    if 'category' in data: share.category_id = data['category']
    if 'title' in data: share.title = data['title']
    if 'content' in data: share.content = data['content']
    if 'quantity' in data: share.quantity = data['quantity']
    if 'location' in data: share.location = data['location']
    if 'trade_time' in data: share.trade_time = data['trade_time']
    if 'deadline' in data: share.deadline = data['deadline']
    share.save()

    return JsonResponse({
        'message': '나눔 수정이 완료되었습니다.',
        'share_id': share.id
    }, status=200)

# 나눔 삭제 페이지
@login_required
@require_http_methods(["DELETE"])
def shares_delete(request, share_id):
    share = get_object_or_404( # 본인만 삭제 가능
        sharingPost,
        pk=share_id,
        host=request.user,
    )
    share.delete()
    return JsonResponse({'message': '성공적으로 삭제되었습니다.'}, status=200)

# 나눔 참여
@login_required
@require_POST
def shares_participate(request, share_id):
    share = get_object_or_404(sharingPost, pk=share_id)
    if share.host == request.user:
        return JsonResponse({'error': '호스트는 참여할 수 없습니다.'}, status=400)
    participation, created = SharingParticipant.objects.get_or_create(
        sharing=share,
        user=request.user,
    )
    if not created:
        return JsonResponse({'error': '이미 참여 신청한 나눔입니다.'}, status=400)

    # 참여 인원 업데이트
    share.current_members += 1
    share.save()

    return redirect('chat:room', pk=share_id)  # 채팅방으로 이동

# 나눔 찜 토글
@login_required
@require_POST
def sharing_wish_toggle(request, share_id):
    share = get_object_or_404(sharingPost, pk=share_id)
    wish  = Wish.objects.filter(user=request.user, sharing=share)
    if wish.exists():
        wish.delete()
        wished = False
    else:
        Wish.objects.create(user=request.user, sharing=share)
        wished = True
    return JsonResponse({'wished': wished})
