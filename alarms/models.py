from django.db import models
from push_notifications.models import GCMDevice, APNSDevice
# Create your models here.


class TvAPNSDevice(APNSDevice):
    version = models.IntegerField()


class TvGCMDevice(GCMDevice):
    version = models.IntegerField()
