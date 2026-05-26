from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from posts.models import *

# ================================================
# 공구
# ================================================
def group_list(request):
    sort = request.GET.get('sort', 'latest')  # 기본값은 마감임박순
    queryset = groupsPost.objects.select_related('host', 'category').prefetch_related('groupImages')

    sort_options = {
        'deadline': 'deadline',  # 마감임박순
        'latest': '-created_at', # 최신순
        'oldest': 'created_at',  # 오래된순
        'price_low': 'price',    # 가격 낮은순
        'price_high': '-price',  # 가격 높은순
    }
    queryset = queryset.order_by(sort_options.get(sort, 'deadline'))

    # 검색
    query = request.GET.get('q', '')
    if query:
        queryset = queryset.filter(title__icontains=query)
    
    # 카테고리 필터
    category_id = request.GET.get('category', '')
    if category_id:
        queryset = queryset.filter(category_id=category_id)

    context = {
        'groups': queryset,
        'categories': Category.objects.all(),
        'sort': sort,
        'query': query,
    }
    return render(request, 'posts/home.html', context)

# 공구 개설 페이지
@login_required
def group_create(request):
    if request.method == 'POST':
        group = groupsPost.objects.create(
            host = request.user,
            category_id = request.POST.get('category'),
            title       = request.POST.get('title'),
            content     = request.POST.get('content'),
            min_members = request.POST.get('min_members'),
            price_per   = request.POST.get('price_per'),
            location    = request.POST.get('location'),
            deadline    = request.POST.get('deadline'),
            link        = request.POST.get('link', ''),
        )
        # 가져온 사용자가 '로그인 했는지' 여부를 가져온다.
        is_authenticated = request.user.is_authenticated
        # 이미지 여러 장 저장
        images = request.FILES.getlist('images')
        for order, image in enumerate(images):
            groupImage.objects.create(group=group, photo=image, order=order)

        return redirect('posts:group_detail', pk=group.pk)

    context = {'categories': Category.objects.all()}
    return render(request, 'posts/group_create.html', context)

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
        'participation_count': group.participantions.filter(status='approved').count(),
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
    group.deadline
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

# ================================================
# 나눔
# ================================================