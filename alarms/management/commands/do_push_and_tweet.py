from django.core.management.base import BaseCommand, CommandError
from push_notifications.models import GCMDevice, APNSDevice
from django.conf import settings
from urllib.request import Request, urlopen, URLError, HTTPError, urlretrieve
from alarms.objects import Channel, Program
from datetime import datetime, timezone
import json
import tweepy


class Command(BaseCommand):
    channels = None
    channel_list_json = None
    default_channels = ['La 1', 'La 2', 'Antena 3', 'Cuatro', 'Telecinco', 'laSexta', 'Teledeporte', 'Clan TVE', 'Canal 24 horas', 'Nova', 'Neox', 'Mega', 'FDF Telecinco', 'Energy', 'Divinity', 'Boing', 'Disney Channel', 'Intereconomía TV', 'Paramount Channel', '13tv', 'Discovery MAX', 'Atreseries', 'Be Mad']
    image_url = 'https://programacion-tv.elpais.com/%s'

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

        title = parameter_json['title']
        id_programa = parameter_json['id_programa']
        channelName = parameter_json['channelName']
        start_time = parameter_json['startTime']
        idCanal = parameter_json['idCanal']
        image = parameter_json['image']

        message_title = '%s, a las %s' % (title, start_time)

        tweet = '%s, a las %s, en %s. %s.' % (title, start_time, channelName,
                                              'https://pelisdeldiaco78.app.link/?programId=%s' % id_programa)
        self.post_tweet(image, tweet)

        for device in GCMDevice.objects.all():
            # self.stdout.write(device.registration_id)
            if device.registration_id != "BLACKLISTED":
                device.send_message(parameter_str)

        for device in APNSDevice.objects.all():
            device.send_message(message_title, sound='default', extra={"message": parameter_str})

    def get_twitter_api(self, cfg):
        auth = tweepy.OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
        auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
        return tweepy.API(auth)

    def post_tweet(self, image_url, message):
        print('posting tweet')
        cfg = {
            "consumer_key": "nQCmiZtepio10sh2SMAQKIqYx",
            "consumer_secret": "0WdgAt3t80YUITbsWG0oPAJPHtRxHmZVetiNeBH9YJZU9m8IMn",
            "access_token": "862601540980412416-XHwxuyIbdlhDK55MqwnYAPr4P7UQCQh",
            "access_token_secret": "WfUPb0DkRlF9ftPz1lcxG1aZzwZawDeJQNmCgDxR3hlpj"
        }

        api = self.get_twitter_api(cfg)

        filename = settings.TMP_DIR + 'temp.jpg'
        try:
            response = urlopen(image_url)
            with open(filename, "wb") as imgFile:
                imgFile.write(response.read())

            status = api.update_with_media(filename, status=message)
            print(status)
        except HTTPError:
            print('image downloading failed, default tweet')
            status = api.update_status(status=message)
            print(status)
