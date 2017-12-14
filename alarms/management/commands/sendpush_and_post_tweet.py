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


    def handle(self, *args, **options):
        self.stdout.write('enter command')

        # Get the channel list from server
        self.channel_list_json = Command.get_channel_list_as_json()
        # created = channel_list_json.get("created", None)
        # data = self.get_data(channel_list_json)
        self.channels = self.get_channel_list(self.channel_list_json)

        all_movies = self.get_grid_data()

        all_programs = self.get_movies_with_rating(all_movies)

        # # for each channel, get all the films to be played
        # for channel in channels:
        #     programs = self.get_channel_programs(channel, data, True)
        #     all_programs.extend(programs)

        all_programs.sort(key=lambda r: (int(r.artistic) + int(r.commercial)), reverse=True)
        # self.stdout.write("******** ordering ********")
        gcm_message = "";

        json_string = json.dumps(all_programs[0], default=lambda o: o.__dict__)
        # json_string = json.dumps([program.__dict__ for program in all_programs])
        # jsonString = json.dumps(all_programs.__dict__)
        # print(json_string)
        # for program in all_programs:
        # jsonString = json.dumps(program.__dict__)
        # self.stdout.write("%s -> %s -> %s" % (program.programTitle, program.startDateTime, program.channel))
        # gcm_message += str("%s -> %s -> %s\n" % (program.program_title, program.start_datetime, program.channel))

        fmt = '%Y-%m-%d %H:%M:%S'
        ini_datetime = datetime.strptime(all_programs[0].iniDate, fmt)

        message_title = '%s, a las %s:%s' % (all_programs[0].get_visible_title(),
                                             ('%02d' % ini_datetime.hour),
                                             ('%02d' % ini_datetime.minute))

        channelName = self.channel_list_json[all_programs[0].idCanal]["nombre"]

        program_image = self.image_url % all_programs[0].image
        tweet = '%s, a las %s:%s, en %s. %s.' % (all_programs[0].get_visible_title(),
                                                 ('%02d' % ini_datetime.hour),
                                                 ('%02d' % ini_datetime.minute),
                                                 channelName,
                                                 'https://pelisdeldiaco78.app.link/?programId=%s' %
                                                 all_programs[0].id_programa)
        for device in GCMDevice.objects.all():
            # self.stdout.write(device.registration_id)
            if device.registration_id != "BLACKLISTED":
                device.send_message(json_string)

        for device in APNSDevice.objects.all():
            device.send_message(message_title, sound='default', extra={"message": json_string})

        self.post_tweet(program_image, tweet)
        self.stdout.write(json_string)
        self.stdout.write('done')

    @staticmethod
    def get_channel_list_as_json():
        """
        # {
        #     "716": {
        #         "id": "716",
        #         "name": "Paramount Channel",
        #         "lang": "SPA",
        #         "order": "21"
        #     },
        #     "841": {
        #         "id": "841",
        #         "name": "Mega",
        #         "lang": "SPA",
        #         "order": "12"
        #     },
        #     "created": "2015-11-12",
        #     "data1029935091": "d6c7ad3fd92f295c7f042a31e15f8438,2fb866e798afe8b0ea7a5fd87a41c85c,55b8c67bf24c5ce95627fd7da8f9318d,71d043c367eeeefc623e902e80ebb75e,5571cb887ee725aeac1520b0c5b0b17f,182ba4d2978bdc4e48f6039bf12db38c,b4a7efcb96a4d56a4c82b4dc1c84662b"
        # }
        :return:
        """
        # Get the dataset
        req = Request('https://programacion-tv.elpais.com/data/canales.json',
                      headers={'User-Agent': 'Mozilla/5.0'})
        # url = 'http://www.mediadata.tv/exports/mediadata/data/channel/list.json'
        response = urlopen(req)

        # Convert bytes to string type and string type to dict
        string = response.read().decode('utf-8')
        json_obj = json.loads(string)
        return json_obj

    def get_data(self, channel_list_json):
        data = next(v for k, v in channel_list_json.items() if k.startswith('data'))
        return data.split(',')[0]

    def get_channel_list(self, channel_list_json):
        channels = []
        for key, value in channel_list_json.items():
            if isinstance(value, dict):
                channel_name = value.get("nombre", None)
                channel_id = value.get("id", None)
                channel = Channel(channel_id, channel_name)
                    # self.stdout.write(channel.name)
                if any(channel_name in s for s in self.default_channels):
                    channels.append(channel)
        return channels

    def get_grid_data(self):
        utc_dt = datetime.now(timezone.utc)
        today_date = utc_dt.strftime("%d%m%Y")

        req = Request('https://programacion-tv.elpais.com/data/parrilla_%s.json'
                      % today_date,
                      headers={'User-Agent': 'Mozilla/5.0'})

        response = urlopen(req)

        # Convert bytes to string type and string type to dict
        string = response.read().decode('utf-8')
        programs_json = json.loads(string)

        programs_array = []

        for channelItem in programs_json:
            # print(channelItem)
            programs_array_json = channelItem.get('programas', None)

            for program_item in programs_array_json:
                description = program_item.get("description", None)
                endDate = program_item.get("endDate", None)
                idCanal = program_item.get("idCanal", None)
                idSection = program_item.get("idSection", None)
                id_programa = program_item.get("id_programa", None)
                iniDate = program_item.get("iniDate", None)
                name = program_item.get("name", None)
                recommended = program_item.get("recommended", None)
                title = program_item.get("title", None)
                txtSection = program_item.get("txtSection", None)

                program = Program(id_programa)

                program.iniDate = str(iniDate)
                program.endDate = str(endDate)
                program.description = description
                program.idCanal = idCanal
                program.idSection = idSection
                program.name = name
                program.recommended = recommended
                program.title = title
                program.txtSection = txtSection

                fmt = '%Y-%m-%d %H:%M:%S'
                ini_datetime = datetime.strptime(program.iniDate, fmt)
                channel_name = self.channel_list_json[idCanal]["nombre"]

                if any(channel_name in s.name for s in self.channels):
                    if txtSection == 'Películas' and ini_datetime.hour > 14:
                        programs_array.append(program)

        return programs_array

    def get_movies_with_rating(self, all_movies):

        programs_array = []
        for movie in all_movies:
            group_id = int(movie.idCanal)

            if movie.get_visible_title() != "":

                req = Request('https://programacion-tv.elpais.com/data/programas/%s.json'
                              % group_id,
                              headers={'User-Agent': 'Mozilla/5.0'})

                response = urlopen(req)

                # Convert bytes to string type and string type to dict
                string = response.read().decode('utf-8')
                programs_json = json.loads(string)

                utc_dt = datetime.now(timezone.utc)
                fmt = '%Y-%m-%d %H:%M:%S'

                for program_json in programs_json:
                    if movie.id_programa == program_json.get('id_programa', None):
                        # print(program_json)

                        artistic = int(program_json.get('artistic', None))
                        commercial = int(program_json.get('commercial', None))
                        image = program_json.get('image', None)

                        movie.artistic = artistic
                        movie.commercial = commercial
                        movie.image = image

                        ini_datetime = datetime.strptime(movie.iniDate, fmt)

                        if utc_dt.day == ini_datetime.day:
                            programs_array.append(movie)
                        break
                    else:
                        continue

        return programs_array

    def get_channel_programs(self, channel, data, only_movies):
        """
            # {
        #     "180895_27249973": {
        #         "id": "180895_27249973",
        #         "channel_id": "841",
        #         "program_id": "180895",
        #         "event_id": "27249973",
        #         "lang": "SPA",
        #         "date_start": "2015-11-12",
        #         "date_end": "2015-11-12",
        #         "start_time": "04:50",
        #         "end_time": "06:55",
        #         "program_title": "El cÃ­rculo secreto",
        #         "section": "Series",
        #         "description": "Cassie se sorprende cuando un amigo del pasado aparece en la puerta de su casa",
        #         "height": "284"
        #     }
        # }



        :param self:
        :param channel:
        :param data:
        :param only_movies:
        :return:
        """
        req = Request('http://www.mediadata.tv/exports/mediadata/data/event/list/channel/%s/date/%s.json'
                      % (channel.channel_id, data),
                      headers={'User-Agent': 'Mozilla/5.0'})
        # url = 'http://www.mediadata.tv/exports/mediadata/data/event/list/channel/%s/date/%s.json' % (channel.channel_id, data)
        response = urlopen(req)

        # Convert bytes to string type and string type to dict
        string = response.read().decode('utf-8')
        programs_json = json.loads(string)

        programs = []
        for key, value in programs_json.items():
            if isinstance(value, dict):
                program_title = value.get("program_title", None)
                program_id = value.get("program_id", None)
                section = value.get("section", None)
                description = value.get("description", None)
                date_start = value.get("date_start", None)
                date_end = value.get("date_end", None)
                start_time = value.get("start_time", None)
                end_time = value.get("end_time", None)
                lang = value.get("lang", None)

                program = Program(program_id, program_title, section, channel.channel_id, lang)

                fmt = '%Y-%m-%d %H:%M'
                program.date_start = str(datetime.strptime('%s %s' % (date_start, start_time), fmt))
                program.description = description
                program.date_start = str(date_start)
                program.date_end = str(date_end)
                program.start_time = str(start_time)
                program.end_time = str(end_time)

                if only_movies:
                    if section == 'Peliculas':
                        # self.stdout.write('%s:  %s' % (program.programTitle, channel.name))
                        self.get_program_details(program)
                        if (program.artistic is not None) and (program.commercial is not None):
                            if (int(program.artistic) >= 4) or (int(program.commercial) >= 4):
                                programs.append(program)
                                # self.stdout.write('%s:  %s -> %s' % (program.program_title, channel.name, program.image))
                else:
                    programs.append(program)
                    self.stdout.write(program.program_title)

        return programs

    def get_program_details(self, program):

        req = Request('http://www.mediadata.tv/exports/mediadata/data/program/%s/%s.json'
                      % (program.lang, program.program_id),
                      headers={'User-Agent': 'Mozilla/5.0'})
        # url = 'http://www.mediadata.tv/exports/mediadata/data/program/%s/%s.json' % (program.lang, program.programId)
        response = urlopen(req)

        # Convert bytes to string type and string type to dict
        string = response.read().decode('utf-8')
        program_json = json.loads(string)
        program.image = program_json.get("image", None)
        program.artistic = program_json.get("artistic", None)
        program.commercial = program_json.get("commercial", None)

        # self.stdout.write(('val-> artistic: %s, commercial: %s' % (program.artistic, program.commercial))

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
