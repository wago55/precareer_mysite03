from .models import Event, User
from .utils import utils


class EventImportError(ImportError):
    pass


class UserImportError(ImportError):
    pass


def do_match():
    try:
        events = Event.objects.all()
    except EventImportError:
        return
    try:
        user_int_lists = [utils.set_int_dict(user, key='user') for user in
                          User.objects.filter(enable_join_matching=True)]
    except UserImportError:
        return

    if len(events) == 0 or len(user_int_lists) == 0:
        return

    for event in events:
        event_int_dict = utils.set_int_dict(event, key='event')
        recommend = []

        for user in user_int_lists:
            """卒業年マッチ"""
            if type(event_int_dict['year']) == int:
                if int(user['year']) == event_int_dict['year']:
                    recommend.append(user['id'])
                    continue
            else:
                if int(user['year']) in event_int_dict['year']:
                    recommend.append(user['id'])
                    continue

            """理文マッチ"""
            if user['s_and_h'] == event_int_dict['s_and_h'] or event_int_dict['s_and_h'] == 0:
                recommend.append(user['id'])
                continue

            """志望業界マッチ"""
            if (event_int_dict['indestry'] == 0 or
                    user['indestry'][0] in event_int_dict['indestry'] or
                    user['indestry'][1] in event_int_dict['indestry'] or
                    user['indestry'][2] in event_int_dict['indestry']):
                recommend.append(user['id'])
                continue

    event.recommend_users = ','.join([str(id) for id in recommend])
    event.save()


def search_possible_event(user_id):
    events = Event.objects.all()
    possible_event = []

    for event in events:
        if event.recommend_users is None:
            continue
        user_list = [int(id) for id in event.recommend_users.split(',')]
        if user_id in user_list:
            possible_event.append(event)

    return possible_event
