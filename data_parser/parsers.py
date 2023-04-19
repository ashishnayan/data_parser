from collections import OrderedDict

from .fields import Field


class BaseDataParser(Field):

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def get_value(self, parser):
        kwargs = parser.__dict__
        added_args = []
        # propagating arguments to nested parsers
        for k, v in kwargs.items():
            if hasattr(self, k) is False:
                setattr(self, k, v)
                added_args.append(k)
        data = self.data
        # removing parsers once data retrieved
        for k in added_args:
            delattr(self, k)
        return data


class DataParserMetaClass(type):

    @classmethod
    def _get_declared_fields(cls, bases, attrs):
        fields = []
        for field_name, obj in list(attrs.items()):
            if isinstance(obj, Field):
                field = attrs.pop(field_name)
                setattr(field, 'field_name', field_name)
                key_name = getattr(field, 'key_name', field_name) or field_name
                setattr(field, 'key_name', key_name)
                fields.append((field_name, field))

        known = set(attrs)

        def visit(name):
            known.add(name)
            return name

        base_fields = [
            (visit(name), f)
            for base in bases if hasattr(base, '_declared_fields')
            for name, f in base._declared_fields.items() if name not in known
        ]

        return OrderedDict(base_fields + fields)

    def __new__(cls, name, bases, attrs):
        attrs['_declared_fields'] = cls._get_declared_fields(bases, attrs)
        return super().__new__(cls, name, bases, attrs)


class DataParser(BaseDataParser, metaclass=DataParserMetaClass):

    @property
    def data(self):
        return {f.key_name: f.get_value(self) for f in self._declared_fields.values()}


# Examples

# def test_method():
#     return "test_method123"
#
#
# class TestParser(DataParser):
#     test_field1 = StaticField("test-data-1")
#     test_field2 = AttributeField(attr="la", property="status")
#     test_field3 = MethodField(test="test")
#     test_field4 = MethodField(method=test_method)
#
#     def get_test_field3(self, test):
#         return f"{test}-got-test-method"
#
#
# class Test1Parser(DataParser):
#     test_parser = TestParser()
#     test_parser_field = StaticField("test-123")
