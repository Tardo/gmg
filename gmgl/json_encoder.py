# GMG Copyright 2022 - Alexandre Díaz
from datetime import datetime
from flask.json import JSONEncoder
from gmgl.utils import date_to_str


class GMGJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                return date_to_str(obj, hours=True, babel=True)
            if isinstance(obj, date):
                return date_to_str(obj, babel=True)
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)
