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
