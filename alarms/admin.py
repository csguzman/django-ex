from django.contrib import admin
from push_notifications.admin import GCMDeviceAdmin, DeviceAdmin
from push_notifications.models import GCMDevice

# # Register your models here.
from alarms.models import TvAPNSDevice, TvGCMDevice

from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()


admin.site.unregister(GCMDevice)


class CustomGCMDeviceAdmin(DeviceAdmin):
    """
    Inherits from DeviceAdmin to handle displaying gcm device as a hex value
    """

    def device_id_hex(self, obj):
        return obj.device_id

    device_id_hex.short_description = "Device ID"

    list_display = ("__unicode__", "device_id_hex", "user", "registration_id", "date_created")


class CustomTvAPNSDevice(DeviceAdmin):
    list_display = ("__unicode__", "device_id", "user", "active", "date_created", "version")
    search_fields = ("name", "device_id", "user__%s" % (User.USERNAME_FIELD), "version")
    list_filter = ("active", "version")
    actions = ("send_message", "send_bulk_message", "prune_devices", "enable", "disable")


class CustomTvGCMDevice(CustomGCMDeviceAdmin):
    """
        Inherits from DeviceAdmin to handle displaying gcm device as a hex value
        """

    def device_id_hex(self, obj):
        return obj.device_id

    device_id_hex.short_description = "Device ID"

    list_display = ("__unicode__", "device_id_hex", "user", "registration_id", "date_created", "version")
    search_fields = ("name", "device_id", "user__%s" % (User.USERNAME_FIELD), "version")
    list_filter = ("active", "version")
    actions = ("send_message", "send_bulk_message", "prune_devices", "enable", "disable")


admin.site.register(GCMDevice, CustomGCMDeviceAdmin)
admin.site.register(TvAPNSDevice, CustomTvAPNSDevice)
admin.site.register(TvGCMDevice, CustomTvGCMDevice)
