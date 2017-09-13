from django.conf.urls import url, include
from django.contrib import admin
from .api import TvAlarmDeviceViewSet, TvAlarmApnsDeviceViewSet
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'device/apns', TvAlarmApnsDeviceViewSet)
router.register(r'device/gcm', TvAlarmDeviceViewSet)

urlpatterns = (url(r'^', include(router.urls)),
               url(r'^admin/', include(admin.site.urls)),
               url(r'device/post_tweet', views.post_tweet_view),
               url(r'device/send_push', views.send_push_view), )
