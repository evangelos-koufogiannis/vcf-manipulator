from django.conf import settings as GLOBAL_SETTINGS
from secrets import compare_digest
from django.core.exceptions import PermissionDenied


def authorize_request(secret):
    if not compare_digest(secret, GLOBAL_SETTINGS.SECRET):
        raise PermissionDenied()


def querydict_to_dict(query_dict):
    data = {}
    for key in query_dict.keys():
        v = query_dict.getlist(key)
        if len(v) == 1:
            v = v[0]
        data[key] = v
    return data