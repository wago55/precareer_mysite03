import math

import numpy as np

from matching.utils.constract import INFO_TO_INT_DICT
from matching.utils.utils import add_other_int


def matching_score(difference: int, max_score=4, do_round=False) -> int:
    """マッチング関数"""
    score = -(math.fabs(difference)) + max_score
    if do_round:
        score = round(score)

    if score <= 0:
        score = 0

    return int(score)


def scoring_for_users(user: list, event: list):
    user = np.asarray(user)
    event = np.asarray(event)

    values = user - event
    result = sum([matching_score(v) for v in values])
    return result


def set_int_list(obj, key=None) -> list:
    if key is None:
        return None
    dict = INFO_TO_INT_DICT[key]

    if key == 'user':
        try:
            d = [
                obj.id,
                add_other_int(dict['sex'], all=False)[obj.sex],
                add_other_int(dict['year'], all=False)[obj.year],
                add_other_int(dict['s_and_h'], all=False)[obj.s_and_h],
                add_other_int(dict['major'], all=False)[obj.major],
                add_other_int(dict['indestry'], all=False)[obj.indestry1],
                add_other_int(dict['indestry'], all=False)[obj.indestry2],
                add_other_int(dict['indestry'], all=False)[obj.indestry3],
                add_other_int(dict['job'], all=False)[obj.job1],
                add_other_int(dict['job'], all=False)[obj.job2],
                add_other_int(dict['job'], all=False)[obj.job3],
                add_other_int(dict['company_type'], all=False)[obj.company_type],
            ]
        except ImportError:
            return None
    if key == 'event':
        try:
            d = [
                obj.id,
                add_other_int(dict['sex'])[obj.sex],
                add_other_int(dict['year'], all=False)[obj.year],
                add_other_int(dict['s_and_h'])[obj.s_and_h],
                add_other_int(dict['major'])[obj.major],
                add_other_int(dict['indestry'])[obj.indestry1],
                add_other_int(dict['indestry'])[obj.indestry2],
                add_other_int(dict['indestry'])[obj.indestry3],
                add_other_int(dict['job'])[obj.job1],
                add_other_int(dict['job'])[obj.job2],
                add_other_int(dict['job'])[obj.job3],
                add_other_int(dict['company_type'])[obj.company_type],
            ]
        except ImportError:
            return None

    return d
