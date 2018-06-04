from enum import Enum


class TypeOption(Enum):
    string =   'string'
    int =      'int'
    float =    'float'
    bool =     'bool'
    dict =     'dict'
    list =     'list'
    datetime = 'datetime'
    date =     'date'


def string_to_type_option(string_type: str) -> TypeOption:
    return {
        'str':      TypeOption.string,
        'int':      TypeOption.int,
        'float':    TypeOption.float,
        'bool':     TypeOption.bool,
        'dict':     TypeOption.dict,
        'list':     TypeOption.list,
        'datetime': TypeOption.datetime,
        'date':     TypeOption.date
    }[string_type]


class SqlAlchemyTypeOption(Enum):
    string =   'String'
    float =    'Float'
    int =      'BigInteger'
    bool =     'Boolean'
    datetime = 'DateTime'
    date =     'Date'


class RestplusTypeOption(Enum):
    string =   'String'
    float =    'Float'
    int =      'Integer'
    bool =     'Boolean'
    datetime = 'DateTime'
    date =     'Date'


def type_option_to_sqlalchemy_type(type_option: TypeOption) -> SqlAlchemyTypeOption:
    return {
        TypeOption.string:   SqlAlchemyTypeOption.string,
        TypeOption.int:      SqlAlchemyTypeOption.int,
        TypeOption.float:    SqlAlchemyTypeOption.float,
        TypeOption.bool:     SqlAlchemyTypeOption.bool,
        TypeOption.datetime: SqlAlchemyTypeOption.datetime,
        TypeOption.date:     SqlAlchemyTypeOption.date,
    }[type_option]


def type_option_to_restplus_type(type_option: TypeOption) -> RestplusTypeOption:
    return {
        TypeOption.string:   RestplusTypeOption.string,
        TypeOption.int:      RestplusTypeOption.int,
        TypeOption.float:    RestplusTypeOption.float,
        TypeOption.bool:     RestplusTypeOption.bool,
        TypeOption.datetime: RestplusTypeOption.datetime,
        TypeOption.date:     RestplusTypeOption.date,
    }[type_option]


class PythonTypeOption(Enum):
    string =   'str'
    float =    'float'
    int =      'int'
    bool =     'bool'
    dict =     'Dict'
    list =     'List'
    datetime = 'datetime'
    date =     'date'


def type_option_to_python_type(type_option: TypeOption) -> PythonTypeOption:
    return {
        TypeOption.string:   PythonTypeOption.string,
        TypeOption.float:    PythonTypeOption.float,
        TypeOption.int:      PythonTypeOption.int,
        TypeOption.bool:     PythonTypeOption.bool,
        TypeOption.dict:     PythonTypeOption.dict,
        TypeOption.list:     PythonTypeOption.list,
        TypeOption.datetime: PythonTypeOption.datetime,
        TypeOption.date:     PythonTypeOption.date,
    }[type_option]


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
    }[type_option]
