import json
from hybrid.element import JSONSerializable
from datetime import datetime


class ElementJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, JSONSerializable):
            return obj.as_dict()
        if isinstance(obj, datetime):
            return obj.__dict__()
        return super().default(obj)

