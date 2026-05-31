from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import ChatRoom, Message

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