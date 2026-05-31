from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from django.http import JsonResponse
from posts.models import *
from posts.forms import GroupPostForm, SharingPostForm
from django.db.models import Case, When, IntegerField, Q
from django.utils.dateparse import parse_datetime
from chat.models import ChatRoom
import json

# ================================================
# 공구
# ================================================
def group_list(request):
    current_sort = request.GET.get('sort', 'latest')

    status_order = Case(
        When(status='recruiting', then=0),
        When(status='closed', then=1),
        When(status='done', then=2),
        default=3,
        output_field=IntegerField(),
    )
    
    sort_options = {
        'deadline': 'deadline',
        'latest': '-created_at',
        'oldest': 'created_at',
        'price_low': 'price_per',
        'price_high': '-price_per',
    }
    
    secondary_sort = sort_options.get(current_sort, '-created_at')

    queryset = (
        groupsPost.objects
        .select_related('host', 'category')
        .prefetch_related('groupImages')
        .annotate(status_order=status_order)
        .order_by('status_order', secondary_sort)
    )

    query = request.GET.get('q', '')
    if query:
        keywords = [kw.strip() for kw in query.split(',') if kw.strip()]
        query_filter = Q()
        for kw in keywords:
            query_filter |= Q(title__icontains=kw)
        queryset = queryset.filter(query_filter)
    
    category_id = request.GET.get('category', '')
    if category_id:
        queryset = queryset.filter(category_id=category_id)
 
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
                group.deadline = parse_datetime(f"{date_str}T{time_str}:00")

            group.save()

            images = request.FILES.getlist('images')
            for order, image in enumerate(images):
                groupImage.objects.create(group=group, photo=image, order=order)

            return redirect('posts:group_detail', group_id=group.pk)
        else:
            print("❌ 공구 개설 폼 검증 실패:", form.errors)
    else:
        form = GroupPostForm()

    return render(request, 'posts/group_create.html', {'form': form, 'categories': Category.objects.all()})


def group_detail(request, group_id):
    group = get_object_or_404(
        groupsPost.objects.select_related('host', 'category').prefetch_related('groupImages', 'groupsParticipants__user'), 
        pk=group_id
    )
    is_participated = False
    is_wished = False

    if request.user.is_authenticated:
        is_participated = groupsParticipant.objects.filter(user=request.user, group=group).exists()
        is_wished = Wish.objects.filter(user=request.user, group=group).exists()

    room = ChatRoom.objects.filter(group_post=group).first()

    context = {
        'group': group,
        'room': room,
        'is_participated': is_participated,
        'participation_count': group.current_members,
        'wish_count': group.wishes.count(),  
        'is_wished': is_wished,              
    }

    return render(request, 'posts/group_detail.html', context)


@login_required
def group_update(request, group_id):
    group = get_object_or_404(groupsPost, pk=group_id, host=request.user)

    if request.method == 'POST':
        form = GroupPostForm(request.POST, request.FILES, instance=group)
        if form.is_valid():
            group = form.save(commit=False)

            date_str = request.POST.get('deadline_date')
            time_str = request.POST.get('deadline_time')
            if date_str and time_str:
                group.deadline = parse_datetime(f"{date_str}T{time_str}:00")
                
            group.save()

            images = request.FILES.getlist('images')
            current_order = group.groupImages.count()
            for order, image in enumerate(images, start=current_order):
                groupImage.objects.create(group=group, photo=image, order=order)

            return redirect('posts:group_detail', group_id=group.pk)
    else:
        form = GroupPostForm(instance=group)
    
    context = {
        'form': form, 
        'group': group,
        'is_update': True, 
        'categories': Category.objects.all(),
    }
    return render(request, 'posts/group_create.html', context)


@login_required
@require_POST
def group_delete(request, group_id):
    group = get_object_or_404(groupsPost, pk=group_id, host=request.user)
    group.delete()
    return JsonResponse({'message': '공구가 성공적으로 삭제되었습니다.'}, status=200)


@login_required
@require_POST
def group_participate(request, room_id):
    from chat.models import ChatRoom

    room = get_object_or_404(ChatRoom, pk=room_id)
    group = room.group_post
    if group.host == request.user:
        return JsonResponse({'error': '호스트는 참여할 수 없습니다.'}, status=400)

    participation, created = groupsParticipant.objects.get_or_create(
        group=group,
        user=request.user,
    )
    if not created:
        return JsonResponse({'error': '이미 참여 신청한 공구입니다.'}, status=400)
    
    group.current_members += 1
    group.save()

    # 해당 공구에 연결된 채팅방 가져오거나 없으면 생성
    room, _ = ChatRoom.objects.get_or_create(
        group_post=group,
        defaults={'name': group.title},
    )

    return redirect('chat:room', room_id=room.id)  # ← room_id로 수정


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
    current_sort = request.GET.get('sort', 'latest')

    status_order = Case(
        When(status='recruiting', then=0),
        When(status='closed', then=1),
        When(status='done', then=2),
        default=3,
        output_field=IntegerField(),
    )

    sort_options = {
        'deadline': 'deadline',
        'latest': '-created_at',
        'oldest': 'created_at',
    }
    secondary_sort = sort_options.get(current_sort, '-created_at')

    queryset = (
        sharingPost.objects
        .select_related('host', 'category')
        .prefetch_related('shareImage')
        .annotate(status_order=status_order)
        .order_by('status_order', secondary_sort)
    )

    query = request.GET.get('q', '')
    if query:
        keywords = [kw.strip() for kw in query.split(',') if kw.strip()]
        query_filter = Q()
        for kw in keywords:
            query_filter |= Q(title__icontains=kw)
        queryset = queryset.filter(query_filter)
    
    category_id = request.GET.get('category', '')
    if category_id:
        queryset = queryset.filter(category_id=category_id)
 
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

            return redirect('posts:share_detail', share_id=share.pk)
        else:
            print("❌ 나눔 개설 폼 검증 실패:", form.errors)
    else:
        form = SharingPostForm()

    return render(request, 'posts/share_create.html', {'form': form, 'categories': Category.objects.all()})


def shares_detail(request, share_id):
    share = get_object_or_404(
        sharingPost.objects.select_related('host', 'category').prefetch_related('shareImage'), 
        pk=share_id
    )
    is_participated = False
    is_wished = False

    if request.user.is_authenticated:
        is_participated = SharingParticipant.objects.filter(user=request.user, sharing=share).exists()
        is_wished = Wish.objects.filter(user=request.user, sharing=share).exists()

    context = {
        'sharing': share,
        'is_participated': is_participated,
        'participation_count': SharingParticipant.objects.filter(sharing=share, status='approved').count(),
        'wish_count': share.wishes.count(),  
        'is_wished': is_wished,
    }

    return render(request, 'posts/share_detail.html', context)


@login_required
def shares_update(request, share_id):
    share = get_object_or_404(sharingPost, pk=share_id, host=request.user)

    if request.method == 'POST':
        form = SharingPostForm(request.POST, request.FILES, instance=share)
        if form.is_valid():
            share = form.save(commit=False)

            date_str = request.POST.get('deadline_date')
            time_str = request.POST.get('deadline_time')
            if date_str and time_str:
                share.deadline = parse_datetime(f"{date_str}T{time_str}:00")

            share.save()

            images = request.FILES.getlist('images')
            current_order = share.shareImage.count()
            for order, image in enumerate(images, start=current_order):
                SharingImage.objects.create(sharing=share, photo=image, order=order)

            return redirect('posts:shares_detail', share_id=share.pk)
    else:
        form = SharingPostForm(instance=share)

    context = {
        'form': form,
        'share': share,
        'is_update': True,
        'categories': Category.objects.all(),
    }
    return render(request, 'posts/share_create.html', context)


@login_required
@require_POST
def shares_delete(request, share_id):
    share = get_object_or_404(sharingPost, pk=share_id, host=request.user)
    share.delete()
    return JsonResponse({'message': '성공적으로 삭제되었습니다.'}, status=200)


@login_required
@require_POST
def shares_participate(request, room_id):
    from chat.models import ChatRoom

    share = get_object_or_404(sharingPost, pk=room_id)
    if share.host == request.user:
        return JsonResponse({'error': '호스트는 참여할 수 없습니다.'}, status=400)

    participation, created = SharingParticipant.objects.get_or_create(
        sharing=share,
        user=request.user,
    )
    if not created:
        return JsonResponse({'error': '이미 참여 신청한 나눔입니다.'}, status=400)

    room, _ = ChatRoom.objects.get_or_create(
        sharing_post=share,
        defaults={'name': share.title},
    )

    return redirect('chat:room', room_id=room.id)  

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