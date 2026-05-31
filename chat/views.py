from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import ChatRoom, Message


def user_can_access_room(user, room):
    if not user.is_authenticated:
        return False

    if room.group_post_id:
        if room.group_post.host_id == user.id:
            return True
        if room.group_post.groupsParticipants.filter(user=user).exclude(status='cancelled').exists():
            return True

    if room.sharing_post_id:
        if room.sharing_post.host_id == user.id:
            return True
        if room.sharing_post.participants.filter(user=user).exclude(status='rejected').exists():
            return True

    return False


def get_room_for_request_user(request, room_id):
    room = get_object_or_404(
        ChatRoom.objects.select_related('group_post', 'sharing_post'),
        id=room_id,
    )
    if not user_can_access_room(request.user, room):
        raise PermissionDenied
    return room


@login_required
def room_list(request):
    f = request.GET.get('filter', 'all')

    rooms = ChatRoom.objects.select_related(
        'group_post', 'sharing_post'
    ).prefetch_related('messages').order_by('-created_at')

    if f == 'recruiting':
        rooms = rooms.filter(
            group_post__status='recruiting'
        ) | rooms.filter(
            sharing_post__status='recruiting'
        )
    elif f == 'done':
        rooms = rooms.filter(
            group_post__status='done'
        ) | rooms.filter(
            sharing_post__status='done'
        )

    return render(request, 'chat/room_list.html', {
        'rooms': rooms,
        'filter': f,
    })

@login_required
def room_detail(request, pk):
    room = get_object_or_404(ChatRoom, id=pk)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(
                room=room,
                user=request.user,
                content=content,
            )
        return redirect('chat:room', id=pk)

    messages = room.messages.select_related('user').order_by('timestamp')
    return render(request, 'chat/room_detail.html', {
        'room': room,
        'messages': messages,
    })

    rooms = (
        ChatRoom.objects
        .filter(
            Q(group_post__host=request.user)
            | Q(group_post__groupsParticipants__user=request.user, group_post__groupsParticipants__status__in=['pending', 'approved'])
            | Q(sharing_post__host=request.user)
            | Q(sharing_post__participants__user=request.user, sharing_post__participants__status__in=['pending', 'approved'])
        )
        .select_related('group_post', 'sharing_post')
        .distinct()
    )
    return render(request, 'chat/room_list.html', {'rooms': rooms})

@login_required
def room_detail(request, room_id):
    room = get_room_for_request_user(request, room_id)
    messages = room.messages.order_by('timestamp')
    return render(request, 'chat/room_detail.html', {'room': room, 'messages': messages})


@login_required
@require_POST
def confirm_purchase(request, room_id):
    room = get_room_for_request_user(request, room_id)
    post = room.group_post or room.sharing_post

    if post is None:
        return JsonResponse({'error': '연결된 게시글이 없습니다.'}, status=400)

    if post.host_id != request.user.id:
        return JsonResponse({'error': '거래 확정 권한이 없습니다.'}, status=403)

    if post.status != 'done':
        post.status = 'done'
        post.save(update_fields=['status', 'updated_at'])

        Message.objects.create(
            room=room,
            user=request.user,
            content='거래가 확정되었습니다.',
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
            return JsonResponse({'error': '방장은 채팅방을 나갈 수 없습니다.'}, status=400)

        with transaction.atomic():
            participant = room.group_post.groupsParticipants.filter(user=request.user).first()
            if participant is None:
                return JsonResponse({'error': '참여 정보를 찾을 수 없습니다.'}, status=404)

            if participant.status != 'cancelled':
                participant.status = 'cancelled'
                participant.save(update_fields=['status', 'updated_at'])

                if room.group_post.current_members > 0:
                    room.group_post.current_members -= 1
                    room.group_post.save(update_fields=['current_members', 'updated_at'])

        return JsonResponse({'status': 'left', 'room_id': room.id})

    if room.sharing_post_id:
        if room.sharing_post.host_id == request.user.id:
            return JsonResponse({'error': '방장은 채팅방을 나갈 수 없습니다.'}, status=400)

        deleted_count, _ = room.sharing_post.participants.filter(user=request.user).delete()
        if deleted_count == 0:
            return JsonResponse({'error': '참여 정보를 찾을 수 없습니다.'}, status=404)

        return JsonResponse({'status': 'left', 'room_id': room.id})

    return JsonResponse({'error': '연결된 게시글이 없습니다.'}, status=400)

