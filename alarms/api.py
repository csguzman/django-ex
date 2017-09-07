from push_notifications.api.rest_framework import APNSDeviceViewSet, GCMDeviceViewSet
from alarms.serializers import TvAlarmDeviceSerializer, TvAlarmDeviceUpdateSerializer, TvAlarmApnsDeviceSerializer, \
    TvAlarmApnsDeviceUpdateSerializer
import logging


# Mixins


class DeviceViewSetMixin(object):
    lookup_field = "registration_id"

    def perform_create(self, serializer):
        # if self.request.user.is_authenticated():
            serializer.save()
        # return super(DeviceViewSetMixin, self).perform_create(serializer)


class TvAlarmDeviceViewSet(DeviceViewSetMixin, GCMDeviceViewSet):
    serializer_class = TvAlarmDeviceSerializer
    http_method_names = ['post']

    def get_serializer_class(self):
        logger = logging.getLogger('TVALARM')
        logger.debug(('GCM ACTION: %s' % self.action))
        logger.debug(('GCM serializer: %s' % self.serializer_class))
        return TvAlarmDeviceSerializer if self.action == "create" else TvAlarmDeviceUpdateSerializer

        # def pre_save(self, obj):
        #     """
        #     Assign the owner of the device before saving it.
        #     :param obj:
        #     :return:
        #     """
        #     obj.user = self.request.user


class TvAlarmApnsDeviceViewSet(DeviceViewSetMixin, APNSDeviceViewSet):
    serializer_class = TvAlarmApnsDeviceSerializer

    def get_serializer_class(self):
        logger = logging.getLogger('TVALARM')
        logger.debug(('APN ACTION: %s' % self.action))

        if self.action == "create":
            logger.debug(('APN serializer: %s' % self.serializer_class))
            return self.serializer_class
        else:
            logger.debug(('APN serializer: %s' % 'TvAlarmApnsDeviceUpdateSerializer'))
            return TvAlarmApnsDeviceUpdateSerializer

            # def pre_save(self, obj):
            #     """
            #     Assign the owner of the device before saving it.
            #     :param obj:
            #     :return:
            #     """
            #     obj.user = self.request.user



