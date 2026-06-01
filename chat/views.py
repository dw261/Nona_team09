from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from .models import ChatRoom, Message


def user_can_access_room(user, room):
    if not user.is_authenticated:
        return False

    if room.group_post_id:
        if room.group_post.host_id == user.id:
            return True
        return room.group_post.groupsParticipants.filter(
            user=user,
            status__in=['pending', 'approved'],
        ).exists()

    if room.sharing_post_id:
        if room.sharing_post.host_id == user.id:
            return True
        return room.sharing_post.participants.filter(
            user=user,
            status__in=['pending', 'approved'],
        ).exists()

    return False


def get_room_for_request_user(request, room_id):
    room = get_object_or_404(
        ChatRoom.objects.select_related('group_post', 'sharing_post'),
        id=room_id,
    )
    if not user_can_access_room(request.user, room):
        raise PermissionDenied
    return room


def get_room_participants(room):
    post = room.group_post or room.sharing_post
    if post is None:
        return []

    users = [post.host]
    if room.group_post_id:
        participants = (
            post.groupsParticipants
            .filter(status__in=['pending', 'approved'])
            .select_related('user')
        )
    else:
        participants = (
            post.participants
            .filter(status__in=['pending', 'approved'])
            .select_related('user')
        )

    seen_ids = {post.host_id}
    for participant in participants:
        if participant.user_id not in seen_ids:
            users.append(participant.user)
            seen_ids.add(participant.user_id)
    return users


@login_required
def room_list(request):
    current_filter = request.GET.get('filter', 'all')
    rooms = (
        ChatRoom.objects
        .filter(
            Q(group_post__host=request.user)
            | Q(group_post__groupsParticipants__user=request.user, group_post__groupsParticipants__status__in=['pending', 'approved'])
            | Q(sharing_post__host=request.user)
            | Q(sharing_post__participants__user=request.user, sharing_post__participants__status__in=['pending', 'approved'])
        )
        .select_related('group_post', 'sharing_post')
        .prefetch_related('messages')
        .distinct()
        .order_by('-created_at')
    )

    if current_filter == 'recruiting':
        rooms = rooms.filter(Q(group_post__status='recruiting') | Q(sharing_post__status='recruiting'))
    elif current_filter == 'done':
        rooms = rooms.filter(Q(group_post__status='done') | Q(sharing_post__status='done'))

    return render(request, 'chat/room_list.html', {
        'rooms': rooms,
        'filter': current_filter,
    })


@login_required
def room_detail(request, room_id):
    room = get_room_for_request_user(request, room_id)
    messages = room.messages.select_related('user').order_by('timestamp')
    participants = get_room_participants(room)
    return render(request, 'chat/room_detail.html', {
        'room': room,
        'messages': messages,
        'participants': participants,
    })


@login_required
@require_POST
def confirm_purchase(request, room_id):
    room = get_room_for_request_user(request, room_id)
    post = room.group_post or room.sharing_post

    if post is None:
        return JsonResponse({'error': '\uc5f0\uacb0\ub41c \uac8c\uc2dc\uae00\uc774 \uc5c6\uc2b5\ub2c8\ub2e4.'}, status=400)

    if post.host_id != request.user.id:
        return JsonResponse({'error': '\uac70\ub798 \ud655\uc815 \uad8c\ud55c\uc774 \uc5c6\uc2b5\ub2c8\ub2e4.'}, status=403)

    if post.status != 'done':
        post.status = 'done'
        post.save(update_fields=['status', 'updated_at'])

        final_price = request.POST.get('final_price', '').strip().replace(',', '')
        message_content = '거래가 확정되었습니다.'
        if final_price.isdigit() and room.group_post_id:
            participant_count = max(len(get_room_participants(room)), 1)
            per_price = int(final_price) // participant_count
            message_content = f'거래가 확정되었습니다. 총 {int(final_price):,}원, 1인당 {per_price:,}원입니다.'

        Message.objects.create(
            room=room,
            user=request.user,
            content=message_content,
        )

    return JsonResponse({
        'status': 'success',
        'room_id': room.id,
        'post_status': post.status,
    })


@login_required
@require_POST
def leave_room(request, room_id):
    room = get_room_for_request_user(request, room_id)

    if room.group_post_id:
        if room.group_post.host_id == request.user.id:
            return JsonResponse({'error': '\ubc29\uc7a5\uc740 \ucc44\ud305\ubc29\uc744 \ub098\uac08 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4.'}, status=400)

        with transaction.atomic():
            participant = room.group_post.groupsParticipants.filter(user=request.user).first()
            if participant is None:
                return JsonResponse({'error': '\ucc38\uc5ec \uc815\ubcf4\ub97c \ucc3e\uc744 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4.'}, status=404)

            if participant.status != 'cancelled':
                participant.status = 'cancelled'
                participant.save(update_fields=['status', 'updated_at'])

                if room.group_post.current_members > 0:
                    room.group_post.current_members -= 1
                    room.group_post.save(update_fields=['current_members', 'updated_at'])

        return JsonResponse({'status': 'left', 'room_id': room.id})

    if room.sharing_post_id:
        if room.sharing_post.host_id == request.user.id:
            return JsonResponse({'error': '\ubc29\uc7a5\uc740 \ucc44\ud305\ubc29\uc744 \ub098\uac08 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4.'}, status=400)

        deleted_count, _ = room.sharing_post.participants.filter(user=request.user).delete()
        if deleted_count == 0:
            return JsonResponse({'error': '\ucc38\uc5ec \uc815\ubcf4\ub97c \ucc3e\uc744 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4.'}, status=404)

        return JsonResponse({'status': 'left', 'room_id': room.id})

    return JsonResponse({'error': '\uc5f0\uacb0\ub41c \uac8c\uc2dc\uae00\uc774 \uc5c6\uc2b5\ub2c8\ub2e4.'}, status=400)
