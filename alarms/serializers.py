from django.db.models import Q
from rest_framework import serializers
from push_notifications.models import GCMDevice, APNSDevice
from push_notifications.api.rest_framework import GCMDeviceSerializer, APNSDeviceSerializer
import logging

from alarms.models import TvAPNSDevice, TvGCMDevice


class TvAlarmDeviceSerializer(GCMDeviceSerializer):

    #device_id_hex = serializers.CharField(source='device_id', read_only=True)

    def validate(self, attrs):
            """
            Validates devices before being registered
            :param attrs:
            :return:
            """
            logger = logging.getLogger('TVALARM')
            deviceid = attrs.get("name")
            logger.debug('checking existing GCM devices...')
            existent_devices = GCMDevice.objects.filter(Q(name=deviceid))
            if len(existent_devices) > 0:
                for device in existent_devices:
                    device.delete()

                # raise serializers.ValidationError(u'There is already a device with that deviceId')

            return attrs

    # def transform_device_id(self, obj, value):
    #     return hex(value)

    class Meta:
        model = TvGCMDevice
        fields = '__all__'


class TvAlarmDeviceUpdateSerializer(TvAlarmDeviceSerializer):
    def validate(self, attrs):
        return attrs


class TvAlarmApnsDeviceSerializer(APNSDeviceSerializer):
    def validate(self, attrs):
            """
            Validates devices before being registered
            :param attrs:
            :return:
            """
            logger = logging.getLogger('TVALARM')
            deviceid = attrs.get("device_id")
            existent_devices = APNSDevice.objects.filter(Q(device_id=deviceid))
            logger.debug('checking existing APN devices...')
            if len(existent_devices) > 0:
                for device in existent_devices:
                    device.delete()

                # raise serializers.ValidationError(u'There is already a device with that deviceId')

            return attrs

    class Meta:
        model = TvAPNSDevice
        fields = '__all__'


class TvAlarmApnsDeviceUpdateSerializer(TvAlarmApnsDeviceSerializer):
    def validate(self, attrs):
        return attrs
