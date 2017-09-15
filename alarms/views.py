from django.contrib.auth.decorators import user_passes_test
from django.core.management import call_command
from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt


@user_passes_test(lambda u: u.is_superuser)
def post_tweet_view(request):
    call_command('post_tweet')
    return HttpResponse(status=200)


@user_passes_test(lambda u: u.is_superuser)
def send_push_view(request):
    call_command('sendpush')
    return HttpResponse(status=200)


@csrf_exempt
def send_push_post_tweet(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_superuser:
                call_command('sendpush_and_post_tweet')
                return HttpResponse(status=200)
