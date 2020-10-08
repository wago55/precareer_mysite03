def add_other_int(d: dict, other=True, all=True, null=True):
    if other:
        int_min = min(d.values())
        d.update({
            '': int_min - 1,
        })
    if all:
        int_max = max(d.values())
        d.update({
            'all': int_max + 1,
        })
    if null:
        int_min = min(d.values())
        d.update({
            'all': int_min - 2,
        })
    return d
