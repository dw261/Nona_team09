from django.shortcuts import redirect


def home(request):
    if request.user.is_authenticated:
        return redirect('posts:group_list')
    return redirect('accounts:welcome')
