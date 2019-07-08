import json
from urllib.request import urlopen, HTTPError
import requests

import facebook
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    facebook_cfg = {
        "page_id": "676790769407022",  # Step 1
        "access_token": "EAAEu8EX3lxgBAL0K3Uq0dmSkm8PVNxQDhvP5LRyzZCYbElC1JjfZAA1frgXMZAQyIbEdHnXkQyyF0p9WgzxkaH0inDI4JRSgOSixh7caZA5mNBUn6a1CglS8LgCgHjlmOVI4vpi0jCoSl3j3farpBUGHMRObf8wW5xmeDiZAiZCQZDZD",  # Step 3
        "page_access_token": "EAAEu8EX3lxgBAMyQRbq2E3iNbM4srYWCQfsFjYuv4Sz27ep3hm3wS95RaT3hKVcITGDMkXLvxNuceGsaFgl62jHGmO3u7C53ztbGR7WHt6UnPOu8x3ZBpVk7e62o3ghbTyZASUc66XKsgT6mpqD9VlvyCp24UTMbPpNZBB8KbX1CEHkpktW"
    }

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
        description = parameter_json['description']
        id_programa = parameter_json['EVENTO']
        channelName = parameter_json['channelName']
        start_time = parameter_json['HORA_INICIO']
        if 'tweetImage' in parameter_json and len(parameter_json["tweetImage"]) != 0:
            tweet_image = parameter_json['tweetImage']

        parameter_json["URL"] += '&id=%s' % id_programa

        print('generating link')
        bodyDict = json.loads(self.dynamic_link_json)
        link = bodyDict["dynamicLinkInfo"]["link"] % id_programa
        bodyDict["dynamicLinkInfo"]["link"] = link
        link = self.generate_dynamic_link(json.dumps(bodyDict))

        tweet = """%s, a las %s, en %s. %s.
        Sinopsis:
        %s
        """ % (title, start_time, channelName, link, description)

        self.post_facebook_page(tweet_image, tweet)

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

    @staticmethod
    def generate_dynamic_link(body):
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

        # graph = facebook.GraphAPI(cfg['access_token'])
        # Get page token to post as the page. You can skip
        # the following if you want to post as yourself.
        # resp = graph.get_object('me/accounts')
        # page_access_token = None
        # for page in resp['data']:
        #     if page['id'] == cfg['page_id']:
        #         page_access_token = page['access_token']
        # graph = facebook.GraphAPI(page_access_token)
        # return graph
        # You can also skip the above if you get a page token:
        # http://stackoverflow.com/questions/8231877/facebook-access-token-for-pages
        # and make that long-lived token as in Step 3
