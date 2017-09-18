class Channel:
    """ class representing a channel """

    def __init__(self, channel_id, name):
        self.channel_id = channel_id
        self.name = name

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


class Program:
    """ class representing a program """


# private String programId;
#   description
#   endDate
#   idCanal
#   idSection
#   id_programa
#   iniDate
#   name
#   recommended
#   title
#   txtSection
#
#
#     /* retrieved in details call */
#     private int artistic;
#     private int commercial;

    def __init__(self, id_programa):
        self.id_programa = id_programa
        self.description = ''
        self.endDate = ''
        self.idCanal = ''
        self.idSection = ''
        self.iniDate = ''
        self.name = ''
        self.recommended = ''
        self.title = ''
        self.txtSection = ''
        self.artistic = 0
        self.commercial = 0
        self.image = ''

    def get_visible_title(self):
        if self.title:
            return self.title
        else:
            return self.name


class ProgramDetails:
    def __init__(self, id_programa):
        self.id_programa = id_programa
        self.actors = ''
        self.artistic = '0'
        self.commercial = '0'
        self.country = ''
        self.creator = ''
        self.description = ''
        self.director = ''
        self.duration = ''
        self.episode = ''
        self.episode_description = ''
        self.episode_title = ''
        self.guest_actors = ''
        self.image = ''
        self.music = ''
        self.photography = ''
        self.poster = ''
        self.presented_by = ''
        self.producer = ''
        self.production = ''
        self.script = ''
        self.season = ''
        self.title = ''
        self.total_episodes = ''
        self.txtParental = ''
        self.txt_genre = ''
        self.txt_section = ''
        self.txt_subgenre = ''
        self.year = ''