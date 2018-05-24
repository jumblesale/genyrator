from enum import Enum
from typing import List, Optional, Dict, Tuple
import attr
import re
import inflection

datetime_regex = re.compile('\d{4}-\d{2}-\d{2}T(\d{2}:)*')


class TypeOption(Enum):
    string =   'string'
    int =      'int'
    float =    'float'
    dict =     'dict'
    list =     'list'
    datetime = 'datetime'


def _string_to_type_option(string_type: str):
    return {
        'str':      TypeOption.string,
        'int':      TypeOption.int,
        'float':    TypeOption.float,
        'dict':     TypeOption.dict,
        'list':     TypeOption.list,
        'datetime': TypeOption.datetime,
    }[string_type]


class SqlAlchemyTypeOption(Enum):
    string =   'String'
    float =    'Float'
    int =      'Integer'
    datetime = 'Datetime'


def _type_option_to_sqlalchemy_type(type_option: TypeOption) -> SqlAlchemyTypeOption:
    return {
        TypeOption.string:   SqlAlchemyTypeOption.string,
        TypeOption.int:      SqlAlchemyTypeOption.int,
        TypeOption.float:    SqlAlchemyTypeOption.float,
        TypeOption.datetime: SqlAlchemyTypeOption.datetime,
    }[type_option]


class PythonTypeOption(Enum):
    string =   'str'
    float =    'float'
    int =      'int'
    dict =     'Dict'
    list =     'List'
    datetime = 'datetime'


def _type_option_to_python_type(type_option: TypeOption) -> PythonTypeOption:
    return {
        TypeOption.string:   PythonTypeOption.string,
        TypeOption.float:    PythonTypeOption.float,
        TypeOption.int:      PythonTypeOption.int,
        TypeOption.dict:     PythonTypeOption.dict,
        TypeOption.list:     PythonTypeOption.list,
        TypeOption.datetime: PythonTypeOption.datetime,
    }[type_option]


def _type_option_to_default_value(type_option: TypeOption) -> str:
    return {
        TypeOption.string:   '""',
        TypeOption.float:    '0.0',
        TypeOption.int:      '0',
        TypeOption.dict:     '{}',
        TypeOption.list:     '[]',
        TypeOption.datetime: '"1970-01-01T00:00"',
    }[type_option]


def _create_padding(padding: int, column_name: str) -> str:
    return ' ' * (padding - len(column_name))


@attr.s
class Column(object):
    name:            str =                  attr.ib()
    camel_case_name: str =                  attr.ib()
    sqlalchemy_type: SqlAlchemyTypeOption = attr.ib()
    python_type:     PythonTypeOption =     attr.ib()
    default:         str =                  attr.ib()
    index:           bool =                 attr.ib()

    def to_dict(self) -> Dict:
        return self.__dict__

    def to_sqlalchemy_model_string(self, padding: int, foreign_key_relationship: Optional[str] = None) -> str:
        if foreign_key_relationship is not None:
            foreign_key = ", db.ForeignKey('{relationship}".format(relationship=foreign_key_relationship)
        else:
            foreign_key = ''
        return '{column_name} ={spacing} db.Column(db.{sql_type}{fk}{index})'.format(
            column_name=self.name, sql_type=self.sqlalchemy_type.value,
            spacing=_create_padding(padding, self.name), fk=foreign_key,
            index=', index=True' if self.index else '',
        )

    def to_type_constructor_argument_string(self, padding: int) -> str:
        return '{name}: {spacing}Optional[{type}]=None,'.format(
            name=self.name, spacing=_create_padding(padding, self.name),
            type=self.python_type.value,
        )

    def to_type_constructor_body_string(self) -> str:
        return '{name}={name} if {name} else {default},'.format(
            name=self.name, default=self.default,
        )

    def to_sqlalchemy_type_constructor_string(self) -> str:
        return '{name}={type}(self.{name}),'.format(
            name=self.name, type=self.python_type.value,
        )

    def to_named_tuple_string(self, padding: int):
        return "        ('{name}', {spacing}{type}),".format(
            name=self.name, spacing=_create_padding(padding, self.name),
            type=self.python_type.value,
        )


@attr.s
class ForeignKey(Column):
    relationship: str = attr.ib()

    def to_sqlalchemy_model_string(self, padding: int, foreign_key_relationship: Optional[str] = None):
        return super().to_sqlalchemy_model_string(padding, self.relationship)


def create_column(name: str, type_option: TypeOption, foreign_key_relationship: Optional[str] = None, index=False) -> Column:
    constructor = Column if foreign_key_relationship is None else ForeignKey
    args = {
        "name":            _camel_case_to_snek_case(name),
        "camel_case_name": _snek_case_to_camel_case(name),
        "sqlalchemy_type": _type_option_to_sqlalchemy_type(type_option),
        "python_type":     _type_option_to_python_type(type_option),
        "default":         _type_option_to_default_value(type_option),
        "index":           index,
    }
    if foreign_key_relationship is not None:
        args["relationship"] = foreign_key_relationship
    return constructor(**args)


def _is_string_date_time_ish(potential_datetime: str) -> bool:
    return bool(datetime_regex.match(potential_datetime))


def _column_from_dict(column_dict: Dict) -> Column:
    type_option = _string_to_type_option(column_dict['type'])
    return create_column(
        name=column_dict['name'],
        type_option=type_option,
        foreign_key_relationship=None
    )


class JoinOption(Enum):
    to_one =  'to_one'
    to_many = 'to_many'


@attr.s
class Relationship(object):
    target_entity_name:           str =        attr.ib()
    target_entity_name_snek_case: str =        attr.ib()
    nullable:                     bool =       attr.ib()
    lazy:                         bool =       attr.ib()
    join:                         JoinOption = attr.ib()
    join_table:                   str =        attr.ib()

    def to_dict(self):
        return self.__dict__

    def to_type_constructor_argument_string(self, padding: int) -> str:
        return '{name}: {spacing}Optional[{type}]=None'.format(
            name=self.target_entity_name_snek_case, spacing=_create_padding(padding, self.target_entity_name_snek_case),
            type=self.target_entity_name
        )

    def to_type_constructor_body_string(self) -> str:
        return '{name}={name} if owner else create_{name}(),'.format(
            name=self.target_entity_name_snek_case
        )

    def to_sqlalchemy_type_constructor_string(self) -> str:
        return '            {name}=self.{name}.to_{name}(),'.format(
            name=self.target_entity_name_snek_case
        )

    def to_sqlalchemy_model_string(self, padding: int) -> str:
        return "    {name} = {spacing}db.relationship('{class_name}', lazy={lazy}, uselist={uselist}{secondary})".format(
            name=self.target_entity_name_snek_case,
            class_name=self.target_entity_name,
            uselist=str(self.join == JoinOption.to_one),
            spacing=_create_padding(padding, self.target_entity_name_snek_case),
            lazy=str(self.lazy),
            secondary=', secondary={}'.format(self.join_table),
        )

    def to_named_tuple_string(self, padding: int):
        return "        ('{name}', {spacing}{type}),".format(
            name=self.target_entity_name_snek_case,
            spacing=_create_padding(padding, self.target_entity_name_snek_case),
            type=self.target_entity_name
        )


def create_relationship(
        target_entity_name: str,
        nullable:           bool,
        lazy:               bool,
        join:               JoinOption,
        join_table:         Optional[str]=None,
) -> Relationship:
    return Relationship(
        target_entity_name=target_entity_name,
        target_entity_name_snek_case=_camel_case_to_snek_case(target_entity_name),
        nullable=nullable,
        lazy=lazy,
        join=join,
        join_table=join_table,
    )


@attr.s
class Entity(object):
    class_name:           str =                attr.ib()
    columns:              List[Column] =       attr.ib()
    class_name_snek_case: str =                attr.ib()
    import_name:          str =                attr.ib()
    column_length:        int =                attr.ib()
    relationships:        List[Relationship] = attr.ib()

    def to_dict(self):
        d = self.__dict__
        d['columns'] = [c.to_dict() for c in self.columns]
        d['relationships'] = [r.to_dict() for r in self.relationships]
        return d

    def to_type_constructor_string(self) -> str:
        column_arguments = [c.to_type_constructor_argument_string(self.column_length) for c in self.columns]
        relationship_arguments = [r.to_type_constructor_argument_string(self.column_length) for r in self.relationships]
        constructor_args = '\n        '.join(column_arguments + relationship_arguments)
        column_body = [c.to_type_constructor_body_string() for c in self.columns]
        relationship_body = [r.to_type_constructor_body_string() for r in self.relationships]
        body_args = '\n        '.join(column_body + relationship_body)
        template = """
def create_{entity_name}(
        {constructor_args}
) -> {class_name}:
    return {class_name}(
        {body_args}
    )
""".format(
            constructor_args=constructor_args,
            entity_name=self.class_name_snek_case,
            body_args=body_args,
            class_name=self.class_name,
        )
        return template

    def to_sqlalchemy_model(self) -> str:
        template = """
class {class_name}(db.Model):  # type: ignore
    id ={spacing}db.Column(db.Integer, primary_key=True)
    {properties}{type_constructor}"""

        columns = '\n    '.join(
            [c.to_sqlalchemy_model_string(self.column_length) for c in self.columns]
        ),
        relationships = '\n    '.join(
            [r.to_sqlalchemy_model_string(self.column_length) for r in self.relationships]
        ),
        return template.format(
            class_name=self.class_name,
            spacing=' ' * (self.column_length - 1),
            properties='\n'.join(columns + relationships),
            type_constructor=self.to_sqlalchemy_type_constructor(),
        )

    def to_sqlalchemy_type_constructor(self) -> str:
        template =\
            """
    def to_{class_name}(self) -> {import_name}:
        return create_{class_name}(
            {properties}
        )
"""
        tab = ' ' * 4
        columns = ('\n' + tab * 3).join(
            [c.to_sqlalchemy_type_constructor_string() for c in self.columns]
        ),
        relationships = ('\n' + tab * 3).join(
            [r.to_sqlalchemy_type_constructor_string() for r in self.relationships]
        ),
        return template.format(
            class_name=self.class_name_snek_case,
            import_name=self.import_name,
            properties='\n'.join(columns + relationships).rstrip(),
        )

    def to_type_string(self):
        properties_join = '\n'
        columns = properties_join.join([c.to_named_tuple_string(self.column_length) for c in self.columns])
        relationships = properties_join.join([r.to_named_tuple_string(self.column_length) for r in self.relationships])
        return "{class_name} = NamedTuple(\n    '{class_name}', [\n{columns}\n{relationships}    ]\n)".format(
            class_name=self.class_name, columns=columns, relationships=relationships,
        )


def _camel_case_to_snek_case(x: str) -> str:
    return inflection.underscore(x)


def _snek_case_to_camel_case(x: str) -> str:
    return inflection.camelize(x, False)


def create_entity(class_name: str, columns: List[Column], relationships: List[Relationship] = []) -> Entity:
    return Entity(
        class_name=class_name,
        class_name_snek_case=_camel_case_to_snek_case(class_name),
        import_name='{}Type'.format(class_name),
        columns=columns,
        # haha 🐍
        column_length=(max(*[
            len(x) for x in
            [c.name for c in columns] +
            [r.target_entity_name_snek_case for r in relationships]]
        )),
        relationships=relationships,
    )


def _entity_from_dict(entity_dict: Dict) -> Entity:
    return create_entity(
        class_name=entity_dict['class_name'],
        columns=[_column_from_dict(x) for x in entity_dict['columns']]
    )


def create_entity_from_exemplar(
        class_name:   str,
        exemplar:     Dict,
        foreign_keys: List[Tuple[str, str]]=list(),
        indexes:      List[str]=list(),
) -> Entity:
    columns = []
    foreign_keys_dict = dict(foreign_keys)
    for k, v in exemplar.items():
        if v is None:
            v = ''
        type_name = type(v).__name__
        type_option = _string_to_type_option(type_name)
        if type_option == TypeOption.string and _is_string_date_time_ish(v):
            type_option = TypeOption.datetime
        foreign_key = foreign_keys_dict[k] if k in foreign_keys_dict else None
        index = k in indexes
        columns.append(create_column(k, type_option, foreign_key, index))
    return create_entity(
        class_name=class_name,
        columns=columns,
    )


def render_db_model(entity: Entity, db_import: str, types_module: str):
    return '{types_import}\n{db_import}\n\n{entity}'.format(
        db_import=db_import,
        entity=entity.to_sqlalchemy_model(),
        types_import='from {module} import {entity_type} as {entity_type}Type, {create_entity}'.format(
            module=types_module, entity_type=entity.class_name,
            create_entity='create_{}'.format(entity.class_name_snek_case)
        ),
    )


def render_type_model(entity: Entity):
    return """from typing import NamedTuple, Optional

{named_tuple}

{tuple_constructor}""".format(
        named_tuple=entity.to_type_string(),
        tuple_constructor=entity.to_type_constructor_string(),
    )


def render_type_constructor(entity: Entity):
    return entity.to_type_constructor_string()
