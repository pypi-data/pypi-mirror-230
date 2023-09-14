import datetime
import decimal
import json
import uuid
import enum
from django.db.models.base import ModelState
from django.db.models.query import QuerySet
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.functional import Promise


class JSONEncoder(json.JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time/timedelta,
    decimal types, generators and other basic python objects.
    """
    def default(self, obj):
        # For Date Time string spec, see ECMA 262
        # https://ecma-international.org/ecma-262/5.1/#sec-15.9.1.15
        if isinstance(obj, Promise):
            return force_str(obj)
        elif isinstance(obj, datetime.datetime):
            return int(obj.timestamp() * 1000)
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, datetime.time):
            if timezone and timezone.is_aware(obj):
                raise ValueError("JSON can't represent timezone-aware times.")
            representation = obj.isoformat()
            return representation
        elif isinstance(obj, datetime.timedelta):
            return str(obj.total_seconds())
        elif isinstance(obj, (decimal.Decimal, uuid.UUID, enum.Enum)):
            return str(obj)
        elif isinstance(obj, QuerySet):
            return tuple(obj)
        elif isinstance(obj, bytes):        # Best-effort for binary blobs.
            return obj.decode()
        elif hasattr(obj, 'tolist'):        # Numpy arrays and array scalars.
            return obj.tolist()
        elif hasattr(obj, '__getitem__'):
            cls = (list if isinstance(obj, (list, tuple)) else dict)
            try:
                return cls(obj)
            except Exception:               # noqa
                pass
        elif hasattr(obj, '__iter__'):      # set, dict views, dict_keys, dict_values, etc.
            return tuple(item for item in obj)
        else:                               # Everything else
            data = obj.__dict__.copy()
            for key, value in obj.__class__.__dict__.items():
                if isinstance(value, property):
                    data[key] = getattr(obj, key)
            return {key: value for key, value in data.items() if not isinstance(value, ModelState)}


# object encode TODO deprecated
class ObjectEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return int(o.timestamp() * 1000)
        elif isinstance(o, (decimal.Decimal, uuid.UUID, enum.Enum)):
            return str(o)
        elif isinstance(o, set):
            return list(o)
        else:
            d = o.__dict__.copy()
            for key, value in o.__class__.__dict__.items():
                if isinstance(value, property):
                    d[key] = getattr(o, key)
            return d


# obj to json
def to_json(obj):
    return json.dumps(obj, cls=JSONEncoder)
