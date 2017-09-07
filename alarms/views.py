from django.contrib.auth.decorators import user_passes_test
from django.core.management import call_command
from django.http import HttpResponse


@user_passes_test(lambda u: u.is_superuser)
def post_tweet_view(request):
    call_command('post_tweet')
    return HttpResponse(status=200)


@user_passes_test(lambda u: u.is_superuser)
def send_push_view(request):
    call_command('post_tweet')
    return HttpResponse(status=200)
