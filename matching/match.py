from . import algo
from .models import Event, User


def do_match():
    events = Event.objects.all()
    event_int_lists = [algo.set_int_list(event, key='event') for event in events]
    user_int_lists = [algo.set_int_list(user, key='user') for user in User.objects.filter(is_student=True)]

    for event_int_list, event in zip(event_int_lists, events):
        rank_num = event.recommend_users_num
        min_score = None
        if rank_num == 0:
            rank_num = 5

        if (len(user_int_lists) <= rank_num or
                event.enable_matching):
            recommend = [user[0] for user in user_int_lists]
        else:
            rank = []
            for user_int_list in user_int_lists:
                rank.append(
                    [user_int_list[0],
                     algo.scoring_for_users(user=user_int_list[1:], event=event_int_list[1:])]
                )
            rank = sorted(rank, key=lambda r: r[-1])
            min_score = rank[rank_num - 1][-1]

            recommend = [data[0] for data in rank[:rank_num]]
            if rank[rank_num][-1] == min_score:
                for user in rank[rank_num + 1:]:
                    if user[-1] != min_score:
                        break
                    else:
                        recommend.append(user[0])

        event.recommend_users = ','.join([str(id) for id in recommend])
        if min_score:
            event.min_matching_score = min_score

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
