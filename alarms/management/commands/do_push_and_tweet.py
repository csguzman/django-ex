import json
from urllib.request import urlopen, HTTPError
import requests

import tweepy
from django.conf import settings
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
        if 'tweetImage' in parameter_json and len(parameter_json["tweetImage"]) != 0:
            tweet_image = parameter_json['tweetImage']

        if 'pushImage' in parameter_json and len(parameter_json["pushImage"]) != 0:
            push_image = parameter_json['pushImage']
        elif 'tweetImage' in parameter_json and len(parameter_json["tweetImage"]) != 0:
            push_image = parameter_json['tweetImage']
        else:
            push_image = ''

        parameter_json["URL"] += '&id=%s' % id_programa
        message_title = '%s, a las %s' % (title, start_time)

        print('generating link')
        bodyDict = json.loads(self.dynamic_link_json)
        link = bodyDict["dynamicLinkInfo"]["link"] % id_programa
        bodyDict["dynamicLinkInfo"]["link"] = link
        link = self.generate_dynamic_link(json.dumps(bodyDict))

        tweet = '%s, a las %s, en %s. %s.' % (title, start_time, channelName, link)
        self.post_tweet(tweet_image, tweet)

        gcm_devices = TvGCMDevice.objects.filter(version__gte=25, cloud_message_type="GCM")\
            .exclude(registration_id="BLACKLISTED")
        gcm_devices.send_message(parameter_str, extra={"image": push_image})

        fcm_devices = TvGCMDevice.objects.filter(version__gte=25, cloud_message_type="FCM") \
            .exclude(registration_id="BLACKLISTED")
        fcm_devices.send_message(parameter_str, use_fcm_notifications=False, extra={"image": push_image})

        apn_devices = TvAPNSDevice.objects.filter(version__gte=25)
        apn_devices.send_message(message_title, sound='default', category='PelisDelDia', mutable_content=1, extra={"message": parameter_str, "image": push_image})


        # for device in TvAPNSDevice.objects.filter(version__gte=25):
        #     device.send_message(message_title, sound='default', extra={"message": parameter_str})

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

    def generate_dynamic_link(self, body):
        url = "https://firebasedynamiclinks.googleapis.com/v1/shortLinks?key=AIzaSyBslo51LLKYhjKCS9rlrrCoi7HvE3HbhJw"
        headers = {
            'Content-Type': 'application/json',
        }
        data = body

        r = requests.post(url, headers=headers, data=data)
        print(r.status_code)
        print(r.json())
        if r.status_code == 200:
            result = r.json()
            return result['shortLink']
        else:
            return ""
