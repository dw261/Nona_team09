from django.contrib.auth.decorators import login_required
from django.db.models import Case, IntegerField, Q, When
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_POST

from chat.models import ChatRoom
from posts.forms import GroupPostForm, SharingPostForm
from posts.models import (
    Category,
    SharingImage,
    SharingParticipant,
    Wish,
    groupImage,
    groupsParticipant,
    groupsPost,
    sharingPost,
)


DEFAULT_CATEGORY_NAMES = ['식품', '생활용품', '밀키트', '신선식품', '기타']


def get_categories():
    if not Category.objects.exists():
        Category.objects.bulk_create(
            [Category(name=name) for name in DEFAULT_CATEGORY_NAMES]
        )
    return Category.objects.all()


def group_list(request):
    current_sort = request.GET.get('sort', 'latest')
    wish_only = request.GET.get('wish') == '1'

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

    queryset = (
        groupsPost.objects
        .select_related('host', 'category')
        .prefetch_related('groupImages')
        .annotate(status_order=status_order)
        .order_by('status_order', sort_options.get(current_sort, '-created_at'))
    )

    query = request.GET.get('q', '')
    if query:
        keywords = [kw.strip() for kw in query.split(',') if kw.strip()]
        query_filter = Q()
        for keyword in keywords:
            query_filter |= Q(title__icontains=keyword)
        queryset = queryset.filter(query_filter)

    category_id = request.GET.get('category', '')
    if category_id:
        queryset = queryset.filter(category_id=category_id)

    wished_ids = []
    if request.user.is_authenticated:
        wished_ids = list(
            request.user.wishes.filter(group__isnull=False).values_list('group_id', flat=True)
        )
        if wish_only:
            queryset = queryset.filter(wishes__user=request.user)
    elif wish_only:
        return redirect(f"{reverse('accounts:login')}?next={request.get_full_path()}")

    wish_toggle_params = request.GET.copy()
    if wish_only:
        wish_toggle_params.pop('wish', None)
    else:
        wish_toggle_params['wish'] = '1'
    wish_toggle_url = request.path
    encoded_wish_toggle_params = wish_toggle_params.urlencode()
    if encoded_wish_toggle_params:
        wish_toggle_url = f'{wish_toggle_url}?{encoded_wish_toggle_params}'

    return render(request, 'posts/group_list.html', {
        'groups': queryset,
        'categories': get_categories(),
        'current_sort': current_sort,
        'sort': current_sort,
        'query': query,
        'wished_ids': wished_ids,
        'wish_only': wish_only,
        'wish_toggle_url': wish_toggle_url,
    })


@login_required
def group_create(request):
    if request.method == 'POST':
        post_data = request.POST.copy()
        if not post_data.get('category'):
            post_data['category'] = get_categories().first().pk
        if not post_data.get('link') and post_data.get('product_url'):
            post_data['link'] = post_data['product_url']
        if post_data.get('price_per'):
            post_data['price_per'] = post_data['price_per'].replace(',', '').replace(' ', '')

        form = GroupPostForm(post_data, request.FILES)
        if form.is_valid():
            group = form.save(commit=False)
            group.host = request.user

            date_str = request.POST.get('deadline_date')
            time_str = request.POST.get('deadline_time')
            if date_str and time_str:
                deadline = parse_datetime(f'{date_str}T{time_str}:00')
                if deadline and timezone.is_naive(deadline):
                    deadline = timezone.make_aware(deadline)
                group.deadline = deadline
            elif not group.deadline:
                group.deadline = timezone.now() + timezone.timedelta(days=1)

            group.save()
            ChatRoom.get_or_create_for_group(group)

            for order, image in enumerate(request.FILES.getlist('images')):
                groupImage.objects.create(group=group, photo=image, order=order)

            return redirect('posts:group_list')

        print('Group create form validation failed:', form.errors)
    else:
        form = GroupPostForm()

    return render(request, 'posts/group_create.html', {
        'form': form,
        'categories': get_categories(),
    })


def group_detail(request, group_id):
    group = get_object_or_404(
        groupsPost.objects.select_related('host', 'category').prefetch_related('groupImages', 'groupsParticipants__user'),
        pk=group_id,
    )
    is_participated = False
    is_wished = False

    if request.user.is_authenticated:
        is_participated = groupsParticipant.objects.filter(
            user=request.user,
            group=group,
            status__in=['pending', 'approved'],
        ).exists()
        is_wished = Wish.objects.filter(user=request.user, group=group).exists()

    room = ChatRoom.objects.filter(group_post=group).first()

    return render(request, 'posts/group_detail.html', {
        'group': group,
        'room': room,
        'is_participated': is_participated,
        'participation_count': group.current_members,
        'wish_count': group.wishes.count(),
        'is_wished': is_wished,
    })


@login_required
def group_update(request, group_id):
    group = get_object_or_404(groupsPost, pk=group_id, host=request.user)

    if request.method == 'POST':
        post_data = request.POST.copy()
        if not post_data.get('link') and post_data.get('product_url'):
            post_data['link'] = post_data['product_url']
        if post_data.get('price_per'):
            post_data['price_per'] = post_data['price_per'].replace(',', '').replace(' ', '')

        form = GroupPostForm(post_data, request.FILES, instance=group)
        if form.is_valid():
            group = form.save(commit=False)

            date_str = request.POST.get('deadline_date')
            time_str = request.POST.get('deadline_time')
            if date_str and time_str:
                deadline = parse_datetime(f'{date_str}T{time_str}:00')
                if deadline and timezone.is_naive(deadline):
                    deadline = timezone.make_aware(deadline)
                group.deadline = deadline

            group.save()
            ChatRoom.get_or_create_for_group(group)

            current_order = group.groupImages.count()
            for order, image in enumerate(request.FILES.getlist('images'), start=current_order):
                groupImage.objects.create(group=group, photo=image, order=order)

            return redirect('posts:group_detail', group_id=group.pk)
    else:
        form = GroupPostForm(instance=group)

    return render(request, 'posts/group_create.html', {
        'form': form,
        'group': group,
        'is_update': True,
        'categories': get_categories(),
    })


@login_required
@require_POST
def group_delete(request, group_id):
    group = get_object_or_404(groupsPost, pk=group_id, host=request.user)
    group.delete()
    return JsonResponse({'message': '\uacf5\uad6c\uac00 \uc131\uacf5\uc801\uc73c\ub85c \uc0ad\uc81c\ub418\uc5c8\uc2b5\ub2c8\ub2e4.'})


@login_required
@require_POST
def group_participate(request, group_id):
    group = get_object_or_404(groupsPost, pk=group_id)

    if group.host == request.user:
        return JsonResponse({'error': '\ud638\uc2a4\ud2b8\ub294 \ucc38\uc5ec\ud560 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4.'}, status=400)

    if group.status != 'recruiting':
        return JsonResponse({'error': '\ubaa8\uc9d1 \uc911\uc778 \uacf5\uad6c\ub9cc \ucc38\uc5ec\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4.'}, status=400)

    participation, created = groupsParticipant.objects.get_or_create(
        group=group,
        user=request.user,
    )

    if not created and participation.status in ['pending', 'approved']:
        return JsonResponse({'error': '\uc774\ubbf8 \ucc38\uc5ec \uc2e0\uccad\ud55c \uacf5\uad6c\uc785\ub2c8\ub2e4.'}, status=400)

    if created:
        group.current_members += 1
        group.save(update_fields=['current_members', 'updated_at'])
    elif participation.status == 'cancelled':
        participation.status = 'pending'
        participation.save(update_fields=['status', 'updated_at'])
        group.current_members += 1
        group.save(update_fields=['current_members', 'updated_at'])

    room, _ = ChatRoom.get_or_create_for_group(group)
    return redirect('chat:room', room_id=room.id)


@login_required
@require_POST
def group_wish_toggle(request, group_id):
    group = get_object_or_404(groupsPost, pk=group_id)
    wish = Wish.objects.filter(user=request.user, group=group)
    if wish.exists():
        wish.delete()
        wished = False
    else:
        Wish.objects.create(user=request.user, group=group)
        wished = True
    return JsonResponse({'wished': wished})


def shares_list(request):
    current_sort = request.GET.get('sort', 'latest')
    wish_only = request.GET.get('wish') == '1'

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

    queryset = (
        sharingPost.objects
        .select_related('host', 'category')
        .prefetch_related('shareImage')
        .annotate(status_order=status_order)
        .order_by('status_order', sort_options.get(current_sort, '-created_at'))
    )

    query = request.GET.get('q', '')
    if query:
        keywords = [kw.strip() for kw in query.split(',') if kw.strip()]
        query_filter = Q()
        for keyword in keywords:
            query_filter |= Q(title__icontains=keyword)
        queryset = queryset.filter(query_filter)

    category_id = request.GET.get('category', '')
    if category_id:
        queryset = queryset.filter(category_id=category_id)

    wished_ids = []
    if request.user.is_authenticated:
        wished_ids = list(
            request.user.wishes.filter(sharing__isnull=False).values_list('sharing_id', flat=True)
        )
        if wish_only:
            queryset = queryset.filter(wishes__user=request.user)
    elif wish_only:
        return redirect(f"{reverse('accounts:login')}?next={request.get_full_path()}")

    wish_toggle_params = request.GET.copy()
    if wish_only:
        wish_toggle_params.pop('wish', None)
    else:
        wish_toggle_params['wish'] = '1'
    wish_toggle_url = request.path
    encoded_wish_toggle_params = wish_toggle_params.urlencode()
    if encoded_wish_toggle_params:
        wish_toggle_url = f'{wish_toggle_url}?{encoded_wish_toggle_params}'

    return render(request, 'posts/share_list.html', {
        'shares': queryset,
        'query': query,
        'current_sort': current_sort,
        'sort': current_sort,
        'categories': get_categories(),
        'wished_ids': wished_ids,
        'wish_only': wish_only,
        'wish_toggle_url': wish_toggle_url,
    })


@login_required
def shares_create(request):
    if request.method == 'POST':
        post_data = request.POST.copy()
        if not post_data.get('category'):
            post_data['category'] = get_categories().first().pk

        form = SharingPostForm(post_data, request.FILES)
        if form.is_valid():
            share = form.save(commit=False)
            share.host = request.user

            date_str = request.POST.get('deadline_date')
            time_str = request.POST.get('deadline_time')
            if date_str and time_str:
                deadline = parse_datetime(f'{date_str}T{time_str}:00')
                if deadline and timezone.is_naive(deadline):
                    deadline = timezone.make_aware(deadline)
                share.deadline = deadline
            elif not share.deadline:
                share.deadline = timezone.now() + timezone.timedelta(days=1)

            share.save()
            ChatRoom.get_or_create_for_share(share)

            for order, image in enumerate(request.FILES.getlist('images')):
                SharingImage.objects.create(sharing=share, photo=image, order=order)

            return redirect('posts:share_list')

        print('Sharing create form validation failed:', form.errors)
    else:
        form = SharingPostForm()

    return render(request, 'posts/share_create.html', {
        'form': form,
        'categories': get_categories(),
    })


def shares_detail(request, share_id):
    share = get_object_or_404(
        sharingPost.objects.select_related('host', 'category').prefetch_related('shareImage'),
        pk=share_id,
    )
    is_participated = False
    is_wished = False

    if request.user.is_authenticated:
        is_participated = SharingParticipant.objects.filter(
            user=request.user,
            sharing=share,
            status__in=['pending', 'approved'],
        ).exists()
        is_wished = Wish.objects.filter(user=request.user, sharing=share).exists()

    room = ChatRoom.objects.filter(sharing_post=share).first()

    return render(request, 'posts/share_detail.html', {
        'sharing': share,
        'room': room,
        'is_participated': is_participated,
        'participation_count': SharingParticipant.objects.filter(sharing=share, status='approved').count(),
        'wish_count': share.wishes.count(),
        'is_wished': is_wished,
    })


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
                deadline = parse_datetime(f'{date_str}T{time_str}:00')
                if deadline and timezone.is_naive(deadline):
                    deadline = timezone.make_aware(deadline)
                share.deadline = deadline

            share.save()
            ChatRoom.get_or_create_for_share(share)

            current_order = share.shareImage.count()
            for order, image in enumerate(request.FILES.getlist('images'), start=current_order):
                SharingImage.objects.create(sharing=share, photo=image, order=order)

            return redirect('posts:share_detail', share_id=share.pk)
    else:
        form = SharingPostForm(instance=share)

    return render(request, 'posts/share_create.html', {
        'form': form,
        'share': share,
        'is_update': True,
        'categories': get_categories(),
    })


@login_required
@require_POST
def shares_delete(request, share_id):
    share = get_object_or_404(sharingPost, pk=share_id, host=request.user)
    share.delete()
    return JsonResponse({'message': '\uc131\uacf5\uc801\uc73c\ub85c \uc0ad\uc81c\ub418\uc5c8\uc2b5\ub2c8\ub2e4.'})


@login_required
@require_POST
def shares_participate(request, share_id):
    share = get_object_or_404(sharingPost, pk=share_id)

    if share.host == request.user:
        return JsonResponse({'error': '\ud638\uc2a4\ud2b8\ub294 \ucc38\uc5ec\ud560 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4.'}, status=400)

    if share.status != 'recruiting':
        return JsonResponse({'error': '\ubaa8\uc9d1 \uc911\uc778 \ub098\ub214\ub9cc \ucc38\uc5ec\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4.'}, status=400)

    participation, created = SharingParticipant.objects.get_or_create(
        sharing=share,
        user=request.user,
    )

    if not created and participation.status in ['pending', 'approved']:
        return JsonResponse({'error': '\uc774\ubbf8 \ucc38\uc5ec \uc2e0\uccad\ud55c \ub098\ub214\uc785\ub2c8\ub2e4.'}, status=400)

    if not created and participation.status == 'rejected':
        participation.status = 'pending'
        participation.save(update_fields=['status', 'updated_at'])

    room, _ = ChatRoom.get_or_create_for_share(share)
    return redirect('chat:room', room_id=room.id)


@login_required
@require_POST
def sharing_wish_toggle(request, share_id):
    share = get_object_or_404(sharingPost, pk=share_id)
    wish = Wish.objects.filter(user=request.user, sharing=share)
    if wish.exists():
        wish.delete()
        wished = False
    else:
        Wish.objects.create(user=request.user, sharing=share)
        wished = True
    return JsonResponse({'wished': wished})
