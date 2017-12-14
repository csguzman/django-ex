from django.contrib.auth.decorators import user_passes_test
from django.core.management import call_command
from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from urllib.request import Request, urlopen, URLError, HTTPError, urlretrieve
from alarms.objects import ProgramDetails
from datetime import datetime, timezone
import json


@user_passes_test(lambda u: u.is_superuser)
def post_tweet_view(request):
    execute_in_background('post_tweet')
    return HttpResponse(status=200)


@user_passes_test(lambda u: u.is_superuser)
def send_push_view(request):
    execute_in_background('sendpush')
    return HttpResponse(status=200)


@user_passes_test(lambda u: u.is_superuser)
def send_push_post_tweet(request):
    execute_in_background('sendpush_and_post_tweet')
    return HttpResponse(status=200)


@user_passes_test(lambda u: u.is_superuser)
def do_push_and_tweet(request):
    parameter = json.dumps(request.GET)
    execute_in_background('do_push_and_tweet', parameter)
    return HttpResponse(status=200)


def execute_command(command_name, parameter):
    if parameter:
        call_command(command_name, parameter)
    else:
        call_command(command_name)


def execute_in_background(command_name, parameter=None):
    import threading
    t = threading.Thread(target=execute_command, args=(command_name, parameter,), kwargs={})
    t.setDaemon(True)
    t.start()


# TODO: needs fixing!
def get_program_details(request):
    program_id = request.GET.get('programId')

    group_id = int(int(program_id) / 10000)

    req = Request('https://programacion-tv.elpais.com/data/programas/%s.json'
                  % group_id,
                  headers={'User-Agent': 'Mozilla/5.0'})

    response = urlopen(req)

    # Convert bytes to string type and string type to dict
    string = response.read().decode('utf-8')
    programs_json = json.loads(string)

    utc_dt = datetime.now(timezone.utc)
    fmt = '%Y-%m-%d %H:%M:%S'
    program_details = None
    for program_json in programs_json:
        if program_id == program_json.get('id_programa', None):
            # print(program_json)
            program_details = ProgramDetails(program_id)

            program_details.actors = program_json.get("actors")

            program_details.artistic = program_json.get('artistic')
            program_details.commercial = program_json.get('commercial')

            program_details.country = program_json.get("country")
            program_details.creator = program_json.get("creator")
            program_details.description = program_json.get("description")
            program_details.director = program_json.get("director")
            program_details.duration = program_json.get("duration")
            program_details.episode = program_json.get("episode")
            program_details.episode_description = program_json.get("episode_description")
            program_details.episode_title = program_json.get("episode_title")
            program_details.guest_actors = program_json.get("guest_actors")
            image = program_json.get('image', None)
            program_details.image = image
            program_details.music = program_json.get("music")
            program_details.photography = program_json.get("photography")
            program_details.poster = program_json.get("poster")
            program_details.presented_by = program_json.get("presented_by")
            program_details.producer = program_json.get("producer")
            program_details.production = program_json.get("production")

            program_details.script = program_json.get("script")
            program_details.season = program_json.get("season")
            program_details.title = program_json.get("title")
            program_details.total_episodes = program_json.get("total_episodes")
            program_details.txtParental = program_json.get("txtParental")
            program_details.txt_genre = program_json.get("txt_genre")
            program_details.txt_section = program_json.get("txt_section")
            program_details.txt_subgenre = program_json.get("txt_subgenre")
            program_details.year = program_json.get("year")
            break

        else:
            continue

    if program_details is not None:
        json_string = json.dumps(program_details.__dict__, ensure_ascii=False)
        details_response = HttpResponse('[' + json_string + ']', content_type='application/json')
        return details_response
    else:
        return HttpResponse(status=404)