from datetime import datetime, date
from enum import Enum
from uuid import UUID


class TypeOption(Enum):
    string =   'string'
    int =      'int'
    float =    'float'
    bool =     'bool'
    dict =     'dict'
    list =     'list'
    datetime = 'datetime'
    date =     'date'
    uuid =     'UUID'


def string_to_type_option(string_type: str) -> TypeOption:
    return {
        'str':      TypeOption.string,
        'int':      TypeOption.int,
        'float':    TypeOption.float,
        'bool':     TypeOption.bool,
        'dict':     TypeOption.dict,
        'list':     TypeOption.list,
        'datetime': TypeOption.datetime,
        'date':     TypeOption.date,
        'UUID':     TypeOption.uuid,
    }[string_type]


def python_type_to_type_option(python_type: Any) -> TypeOption:
    return {
        str:      TypeOption.string,
        int:      TypeOption.int,
        float:    TypeOption.float,
        bool:     TypeOption.bool,
        dict:     TypeOption.dict,
        list:     TypeOption.list,
        datetime: TypeOption.datetime,
        date:     TypeOption.date,
        UUID:     TypeOption.uuid,
    }[python_type]


def type_option_to_type_constructor(type_option: TypeOption):
    return {
        TypeOption.string:   str,
        TypeOption.int:      int,
        TypeOption.float:    float,
        TypeOption.bool:     bool,
        TypeOption.dict:     dict,
        TypeOption.list:     list,
        TypeOption.datetime: str,
        TypeOption.date:     str,
        TypeOption.uuid:     str,
    }[type_option]


class SqlAlchemyTypeOption(Enum):
    string =   'db.String'
    float =    'db.Float'
    int =      'db.BigInteger'
    bool =     'db.Boolean'
    datetime = 'db.DateTime'
    date =     'db.Date'
    uuid =     'UUIDType'


class RestplusTypeOption(Enum):
    string =   'String'
    float =    'Float'
    int =      'Integer'
    bool =     'Boolean'
    datetime = 'DateTime'
    date =     'Date'
    uuid =     'String'


def type_option_to_sqlalchemy_type(type_option: TypeOption) -> SqlAlchemyTypeOption:
    return getattr(SqlAlchemyTypeOption, type_option.value)


def type_option_to_restplus_type(type_option: TypeOption) -> RestplusTypeOption:
    return getattr(RestplusTypeOption, type_option.value)


class PythonTypeOption(Enum):
    string =   'str'
    float =    'float'
    int =      'int'
    bool =     'bool'
    dict =     'Dict'
    list =     'List'
    datetime = 'datetime'
    date =     'date'
    uuid =     'UUID'


def type_option_to_python_type(type_option: TypeOption) -> PythonTypeOption:
    return getattr(PythonTypeOption, type_option.value)


def type_option_to_default_value(type_option: TypeOption) -> str:
    return {
        TypeOption.string:   '""',
        TypeOption.float:    '0.0',
        TypeOption.int:      '0',
        TypeOption.bool:     'None',
        TypeOption.dict:     '{}',
        TypeOption.list:     '[]',
        TypeOption.datetime: '"1970-01-01T00:00"',
        TypeOption.date:     '"1970-01-01T00:00"',
        TypeOption.uuid:     '"00000000-0000-0000-0000-000000000000"',
    }[type_option]
