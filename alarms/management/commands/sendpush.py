import json

from django.core.management.base import BaseCommand

from alarms.models import TvGCMDevice, TvAPNSDevice


class Command(BaseCommand):
    channels = None
    channel_list_json = None
    default_channels = ['La 1', 'La 2', 'Antena 3', 'Cuatro', 'Telecinco', 'laSexta', 'Teledeporte', 'Clan TVE', 'Canal 24 horas', 'Nova', 'Neox', 'Mega', 'FDF Telecinco', 'Energy', 'Divinity', 'Boing', 'Disney Channel', 'Intereconomía TV', 'Paramount Channel', '13tv', 'Discovery MAX', 'Atreseries', 'Be Mad']
    image_url = 'https://programacion-tv.elpais.com/%s'

    dynamic_link_json = "{\"dynamicLinkInfo\": {\"dynamicLinkDomain\": \"e2ays.app.goo.gl\",\"link\": \"https://pelisdeldia.com/?programId=%s\",\"androidInfo\": {\"androidPackageName\": \"com.csalguero.onlymovies\",\"androidFallbackLink\": \"https://play.google.com/store/apps/details?id=com.csalguero.onlymovies\"},\"iosInfo\": {\"iosBundleId\": \"com.csalguero.onlymovies\",\"iosFallbackLink\": \"https://itunes.apple.com/es/app/apple-store/id1235072016\",\"iosAppStoreId\": \"1235072016\"}},\"suffix\": {\"option\": \"SHORT\"}}"

    def add_arguments(self, parser):
        parser.add_argument('parameter', nargs='+', type=str)

# programId
# title
# time
# channel
# imageUrl
    def handle(self, *args, **options):
        self.stdout.write('enter command')
        parameter_str = options['parameter'][0]
        self.stdout.write('parameters:  %s' % parameter_str)
        parameter_json = json.loads(parameter_str)
        title = parameter_json['TITULO']
        id_programa = parameter_json['EVENTO']
        channelName = parameter_json['channelName']
        start_time = parameter_json['HORA_INICIO']

        if 'pushImage' in parameter_json and len(parameter_json["pushImage"]) != 0:
            push_image = parameter_json['pushImage']

        parameter_json["URL"] += '&id=%s' % id_programa
        message_title = '%s, a las %s' % (title, start_time)

        print('generating link')
        bodyDict = json.loads(self.dynamic_link_json)
        link = bodyDict["dynamicLinkInfo"]["link"] % id_programa
        bodyDict["dynamicLinkInfo"]["link"] = link

        gcm_devices = TvGCMDevice.objects.filter(version__gte=25, cloud_message_type="GCM")\
            .exclude(registration_id="BLACKLISTED")
        gcm_devices.send_message(parameter_str, extra={"image": push_image})

        fcm_devices = TvGCMDevice.objects.filter(version__gte=25, cloud_message_type="FCM") \
            .exclude(registration_id="BLACKLISTED")
        fcm_devices.send_message(parameter_str, use_fcm_notifications=False, extra={"image": push_image})

        apn_devices = TvAPNSDevice.objects.filter(version__gte=25)
        apn_devices.send_message(message_title, sound='default', category='PelisDelDia', mutable_content=1, extra={"message": parameter_str, "image": push_image})