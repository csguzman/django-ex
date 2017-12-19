from django.contrib import admin
from push_notifications.admin import GCMDeviceAdmin, DeviceAdmin
from push_notifications.models import GCMDevice

# # Register your models here.
from alarms.models import TvAPNSDevice, TvGCMDevice

admin.site.unregister(GCMDevice)


class CustomGCMDeviceAdmin(DeviceAdmin):
    """
    Inherits from DeviceAdmin to handle displaying gcm device as a hex value
    """

    def device_id_hex(self, obj):
        return obj.device_id

    device_id_hex.short_description = "Device ID"

    list_display = ("__unicode__", "device_id_hex", "user", "registration_id", "date_created")

admin.site.register(GCMDevice, CustomGCMDeviceAdmin)
admin.site.register(TvAPNSDevice)
admin.site.register(TvGCMDevice)
