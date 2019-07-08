import json
from urllib.request import urlopen, HTTPError
import requests

import tweepy
import facebook
from django.conf import settings
from django.core.management.base import BaseCommand

from alarms.models import TvGCMDevice, TvAPNSDevice


class Command(BaseCommand):
    channels = None
    channel_list_json = None
    dynamic_link_json = "{\"dynamicLinkInfo\": {\"dynamicLinkDomain\": \"e2ays.app.goo.gl\",\"link\": \"https://pelisdeldia.com/?programId=%s\",\"androidInfo\": {\"androidPackageName\": \"com.csalguero.onlymovies\",\"androidFallbackLink\": \"https://play.google.com/store/apps/details?id=com.csalguero.onlymovies\"},\"iosInfo\": {\"iosBundleId\": \"com.csalguero.onlymovies\",\"iosFallbackLink\": \"https://itunes.apple.com/es/app/apple-store/id1235072016\",\"iosAppStoreId\": \"1235072016\"}},\"suffix\": {\"option\": \"SHORT\"}}"
    facebook_cfg = {
        "page_id": "676790769407022",  # Step 1
        "access_token": "EAAEu8EX3lxgBAL0K3Uq0dmSkm8PVNxQDhvP5LRyzZCYbElC1JjfZAA1frgXMZAQyIbEdHnXkQyyF0p9WgzxkaH0inDI4JRSgOSixh7caZA5mNBUn6a1CglS8LgCgHjlmOVI4vpi0jCoSl3j3farpBUGHMRObf8wW5xmeDiZAiZCQZDZD",
        # Step 3
        "page_access_token": "EAAEu8EX3lxgBAMyQRbq2E3iNbM4srYWCQfsFjYuv4Sz27ep3hm3wS95RaT3hKVcITGDMkXLvxNuceGsaFgl62jHGmO3u7C53ztbGR7WHt6UnPOu8x3ZBpVk7e62o3ghbTyZASUc66XKsgT6mpqD9VlvyCp24UTMbPpNZBB8KbX1CEHkpktW"
    }

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
        description = parameter_json['description']
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

        post = """%s, a las %s, en %s. %s.
        Sinopsis:
        %s
        """ % (title, start_time, channelName, link, description)
        self.post_facebook_page(tweet_image, post)

        gcm_devices = TvGCMDevice.objects.filter(version__gte=25, cloud_message_type="GCM")\
            .exclude(registration_id="BLACKLISTED")
        gcm_devices.send_message(parameter_str, extra={"image": push_image})

        fcm_devices = TvGCMDevice.objects.filter(version__gte=25, cloud_message_type="FCM") \
            .exclude(registration_id="BLACKLISTED")
        fcm_devices.send_message(parameter_str, use_fcm_notifications=False, extra={"image": push_image})

        apn_devices = TvAPNSDevice.objects.filter(version__gte=25)
        apn_devices.send_message(message_title, sound='default', category='PelisDelDia', mutable_content=1, extra={"message": parameter_str, "image": push_image})

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

    def post_facebook_page(self, image_url, message):
        api = self.get_api(self.facebook_cfg)

        filename = settings.TMP_DIR + 'temp.jpg'
        try:
            response = urlopen(image_url)
            with open(filename, "wb") as imgFile:
                imgFile.write(response.read())

            # status = api.put_photo(image=filename, message=message)
            status = api.put_photo(open(filename, 'rb'), message=message)
            # post_status = api.put_object(parent_object="me",
            #                              connection_name="feed",
            #                              message=message)
            print(status)

        except facebook.GraphAPIError as e:
            print(e)
            print('Facebook post failed')

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

    @staticmethod
    def get_api(cfg):
        graph = facebook.GraphAPI(cfg['page_access_token'])
        return graph
