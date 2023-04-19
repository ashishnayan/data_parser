import datetime
import logging

import pytz

logger = logging.getLogger(__name__)


def get_property(obj, key, default=None, raise_exception: bool = False):
    if key[0] == "'":
        _key = key.split("'.", 1)
        _key[0] = _key[0][1:]
        if _key[0][-1] == "'":
            _key[0] = _key[0][:-1]
    else:
        _key = key.split(".", 1)
    k = _key[0]
    if isinstance(obj, (dict, list, tuple)):
        try:
            k = int(k) if isinstance(obj, (
                list,
                tuple,
            )) else k
            _obj = obj[k]
        except Exception as e:
            logger.warn(f"Invalid Argument {k}")
            if raise_exception is True:
                raise Exception(e)
            return default
    elif hasattr(obj, k):
        _obj = getattr(obj, k)
    else:
        if raise_exception is True:
            raise AttributeError(f"type object '{obj.__class__.__name__}' has no attribute '{k}'")
        return default
    if len(_key) == 1:
        return _obj
    return get_property(_obj, _key[1], default, raise_exception)


def now(timezone: str = None):
    tz = pytz.utc if timezone is None else pytz.timezone(timezone)
    return datetime.datetime.utcnow().replace(tzinfo=tz)


def format_datetime(value: datetime.datetime = None, date_format: str = None, timezone: str = None):
    value = value or now()
    if timezone is not None:
        tz = pytz.timezone(timezone)
        value = value.astimezone(tz)
    return value.isoformat() if date_format is None else value.strftime(date_format)
