from typing import Any, Callable, Optional

from .utils import format_datetime, get_property


class Field:

    def __init__(self, key_name: str = None):
        self.key_name = key_name

    def get_value(self, parser):
        raise NotImplementedError


class StaticField(Field):

    def __init__(self, val: Any, key_name: str = None):
        super().__init__(key_name=key_name)
        self.val = val

    def get_value(self, parser):
        return self.val


class AttributeField(Field):

    def __init__(self, attr: str, property: str = None, default: Any = None,
                 raise_exception: bool = False,
                 formatter: Optional[Callable] = None,
                 key_name: str = None, **kwargs):
        super().__init__(key_name=key_name)
        self.attr = attr
        self.property = property
        self.default = default
        self.raise_exception = raise_exception
        self.formatter = formatter
        self.kwargs = kwargs

    def get_value(self, parser):
        if hasattr(parser, self.attr) is False and self.raise_exception is True:
            raise AttributeError(f"type object '{parser.__class__.__name__}' has no attribute '{self.attr}'")
        obj = getattr(parser, self.attr, None)
        if obj is None:
            return self.default
        if self.property is None:
            return obj

        value = get_property(obj, self.property, self.default, self.raise_exception)
        if self.formatter is not None:
            kwargs = self.kwargs or {}
            return self.formatter(value, **kwargs)
        return value


class MethodField(Field):

    def __init__(self, method: Optional[str] = None, key_name: str = None, **kwargs):
        super().__init__(key_name=key_name)
        self.method = method
        self.kwargs = kwargs

    def get_value(self, parser):
        method_name = self.method or f"get_{self.field_name}"
        method = getattr(parser, method_name)
        return method(**self.kwargs)


class CurrentDatetimeField(Field):

    def __init__(self, date_format: str = "%d-%m-%Y %H:%M:%S", timezone: str = "UTC",
                 key_name: str = None):
        super().__init__(key_name=key_name)
        self.date_format = date_format
        self.timezone = timezone

    def get_value(self, parser):
        return format_datetime(date_format=self.date_format, timezone=self.timezone)


class AttributeDatetimeField(AttributeField):

    def __init__(self, attr: str, property: str, default: Any = None,
                 raise_exception: bool = False,
                 date_format: str = "%d-%m-%Y %H:%M:%S", timezone: str = "UTC",
                 key_name: str = None):
        super().__init__(attr, property, default, raise_exception, key_name=key_name,
                         formatter=format_datetime, date_format=date_format, timezone=timezone
                         )


class AttributeDateField(AttributeField):

    def __init__(self, attr: str, property: str, default: Any = None,
                 raise_exception: bool = False,
                 date_format: str = "%d-%m-%Y",
                 key_name: str = None):
        super().__init__(attr, property, default, raise_exception, key_name=key_name,
                         formatter=format_datetime, date_format=date_format, timezone=None
                         )
