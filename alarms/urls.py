from django.conf.urls import url, include
from django.contrib import admin
from .api import TvAlarmDeviceViewSet, TvAlarmApnsDeviceViewSet
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'device/apns', TvAlarmApnsDeviceViewSet)
router.register(r'device/gcm', TvAlarmDeviceViewSet)

urlpatterns = (url(r'^', include(router.urls)),
               url(r'^admin/', admin.site.urls),
               url(r'device/send_push_post_tweet', views.send_push_post_tweet),
               url(r'device/post_tweet', views.post_tweet_view),
               url(r'device/send_push', views.send_push_view),
               url(r'device/do_push_tweet', views.do_push_and_tweet),
               url(r'program_details', views.get_program_details),)
