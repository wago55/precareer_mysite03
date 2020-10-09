import ast

from .constract import S_AND_H_TO_INT


def category_add_all(category: list):
    if ('all', '指定なし') in category:
        return category
    category.append(('all', '指定なし'), )
    return category


def is_all(v):
    if type(v) == int:
        return v
    else:
        return 0


def get_target_year(v: str):
    l1 = v.split("\'")
    if len(l1) == 1:
        return int(l1[0])
    s = ''.join(l1)
    l2 = ast.literal_eval(s)
    return tuple(l2)


def set_int_dict(obj, key=None) -> dict:
    if key is None:
        return None

    if key == 'user':
        try:
            d = {
                'id': obj.id,
                'year': obj.year,
                's_and_h': S_AND_H_TO_INT[obj.s_and_h],
                'indestry': [obj.indestry1, obj.indestry2, obj.indestry3]
            }
        except ImportError:
            return None
    if key == 'event':
        try:
            d = {
                'id': obj.id,
                'year': get_target_year(obj.year),
                's_and_h': is_all(S_AND_H_TO_INT[obj.s_and_h]),
                'indestry': tuple([is_all(obj.indestry1), is_all(obj.indestry2), is_all(obj.indestry3)])
            }
        except ImportError:
            return None

    return d
