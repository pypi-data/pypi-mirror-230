from datetime import timedelta
from string import Template

class TimeDeltaTemplate(Template):
    delimiter = "%"
    idpattern = "(?a-i:[wdHMSf])" # ASCII-only, don't ignore case

def strftime(td, fmt):
    if not isinstance(td, timedelta):
        return f'{td:{fmt}}'
    
    units = {
        'w': (timedelta(weeks=1), None),
        'd': (timedelta(days=1), None),
        'H': (timedelta(hours=1), 2),
        'M': (timedelta(minutes=1), 2),
        'S': (timedelta(seconds=1), 2),
        'f': (timedelta(microseconds=1), 6),
    }
    template = TimeDeltaTemplate(fmt)
    
    identifiers = []
    for unit in units:
        try:
            template.substitute({k: '' for k in units if k != unit})
        except KeyError:
            identifiers.append(unit)
    # identifiers = template.get_identifiers() # available only in 3.11+

    d = {}
    for unit, (unit_td, unit_padding) in units.items():
        if unit in identifiers:
            q, td = divmod(td, unit_td)
            d[unit] = str(q) if unit_padding is None else f'{q:0{unit_padding}d}'

    return template.substitute(d)