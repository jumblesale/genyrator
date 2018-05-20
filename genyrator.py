import json
from enum import Enum
from typing import List, Optional, Dict
import attr


class TypeOption(Enum):
    string = 'string'
    int =    'int'
    float =  'float'
    dict =   'dict'
    list =   'list'


def _string_to_type_option(string_type: str):
    return {
        'str':   TypeOption.string,
        'int':   TypeOption.int,
        'float': TypeOption.float,
        'dict':  TypeOption.dict,
        'list':  TypeOption.list,
    }[string_type]


class SqlAlchemyTypeOption(Enum):
    string = 'String'
    float =  'Float'
    int =    'Integer'


def _type_option_to_sql_alchemy_type(type_option: TypeOption) -> SqlAlchemyTypeOption:
    return {
        TypeOption.string: SqlAlchemyTypeOption.string,
        TypeOption.int:    SqlAlchemyTypeOption.int,
        TypeOption.float:  SqlAlchemyTypeOption.float,
    }[type_option]


class PythonTypeOption(Enum):
    string = 'str'
    float =  'float'
    int =    'int'
    dict =   'Dict'
    list =   'List'


def _type_option_to_python_type(type_option: TypeOption) -> PythonTypeOption:
    return {
        TypeOption.string: PythonTypeOption.string,
        TypeOption.float:  PythonTypeOption.float,
        TypeOption.int:    PythonTypeOption.int,
        TypeOption.dict:   PythonTypeOption.dict,
        TypeOption.list:   PythonTypeOption.list,
    }[type_option]


def _type_option_to_default_value(type_option: TypeOption) -> str:
    return {
        TypeOption.string: '""',
        TypeOption.float:  '0.0',
        TypeOption.int:    '0',
        TypeOption.dict:   '{}',
        TypeOption.list:   '[]',
    }[type_option]


@attr.s
class Column(object):
    name:             str =                  attr.ib()
    sql_alchemy_type: SqlAlchemyTypeOption = attr.ib()
    python_type:      PythonTypeOption =     attr.ib()
    default:          str =                  attr.ib()

    def to_dict(self):
        return self.__dict__


def create_column(name: str, type_option: TypeOption) -> Column:
    return Column(
        name=name,
        sql_alchemy_type=_type_option_to_sql_alchemy_type(type_option),
        python_type=_type_option_to_python_type(type_option),
        default=_type_option_to_default_value(type_option),
    )


def _column_from_dict(column_dict: Dict) -> Column:
    type_option = _string_to_type_option(column_dict['type'])
    return create_column(
        name=column_dict['name'],
        type_option=type_option,
    )


class JoinOption(Enum):
    to_one =  'to_one'
    to_many = 'to_many'


@attr.s
class Relationship(object):
    target_entity_name: str =           attr.ib()
    target_entity_name_snek_case: str = attr.ib()
    nullable: bool =                    attr.ib()
    lazy: bool =                        attr.ib()
    join: JoinOption =                  attr.ib()

    def to_dict(self):
        return self.__dict__


def create_relationship(
        target_entity_name: str,
        nullable:           bool,
        lazy:               bool,
        join:               JoinOption,
) -> Relationship:
    return Relationship(
        target_entity_name=target_entity_name,
        target_entity_name_snek_case=_camel_case_to_snek_case(target_entity_name),
        nullable=nullable,
        lazy=lazy,
        join=join,
    )


@attr.s
class Entity(object):
    class_name: str =                   attr.ib()
    columns: List[Column] =             attr.ib()
    class_name_snek_case: str =         attr.ib()
    import_name: str =                  attr.ib()
    column_length: int =                attr.ib()
    relationships: List[Relationship] = attr.ib()

    def to_dict(self):
        d = self.__dict__
        d['columns'] = [c.to_dict() for c in self.columns]
        d['relationships'] = [r.to_dict() for r in self.relationships]
        return d


def _camel_case_to_snek_case(x: str) -> str:
    return x.lower()


def create_entity(class_name: str, columns: List[Column], relationships: List[Relationship]=[]) -> Entity:
    return Entity(
        class_name=class_name,
        class_name_snek_case=_camel_case_to_snek_case(class_name),
        import_name='{}Type'.format(class_name),
        columns=columns,
        # haha 🐍
        column_length=(max(*[len(x) for x in [c.name for c in columns]])),
        relationships=relationships,
    )


def _entity_from_dict(entity_dict: Dict) -> Entity:
    return create_entity(
        class_name=entity_dict['class_name'],
        columns=[_column_from_dict(x) for x in entity_dict['columns']]
    )


def _entity_from_exemplar(class_name: str, exemplar: Dict) -> Entity:
    columns = []
    for k, v in exemplar.items():
        type_option = _string_to_type_option(type(v).__name__)
        columns.append(create_column(k, type_option))
    return create_entity(
        class_name=class_name,
        columns=columns,
    )


db_model_template = """
class {{ entity.class_name }}(db.Model):  # type: ignore
{%- set padding = entity.column_length - ('id'|length) %}
    id ={%for i in range(0, padding)%} {%endfor%} db.Column(db.Integer, primary_key=True)
{%- for column in entity.columns %}
{%- set padding = entity.column_length - (column['name']|length) %}
    {{ column.name }} ={%for i in range(0, padding)%} {%endfor%} db.Column(db.{{ column.sql_alchemy_type.value }})
{%- endfor %}
{%- for relationship in entity.relationships %}
{%- set padding = entity.column_length - (relationship.target_entity_name_snek_case|length) %}
    {{ relationship.target_entity_name_snek_case }} = {%for i in range(0, padding)%} {%endfor%}db.relationship('{{ relationship.target_entity_name }}', lazy={{ "" ~ relationship.lazy }}{%if relationship.join.value == 'to_one'%}, uselist=False{%endif%})
{%- endfor %}

    def to_json(self) -> Dict:
        d = {
{%- for column in entity.columns %}
{%- set padding = entity.column_length - (column['name']|length) %}
            "{{ column.name }}": {%for i in range(0, padding)%} {%endfor%}{{ column.python_type.value }}(self.{{ column.name }}),
{%- endfor %}
        }
{%- for relationship in entity.relationships %}
        d['{{ relationship.target_entity_name_snek_case }}'] = self.{{ relationship.target_entity_name_snek_case }}.to_{{ relationship.target_entity_name_snek_case }}()
{%- endfor %}
        return d
"""

named_tuple_template = """
{{ entity.class_name }} = NamedTuple(
    '{{ entity.class_name }}', [
{%- for column in entity.columns %}
{%- set padding = entity.column_length - (column.name|length) %}
        ('{{ column.name }}', {%for i in range(0, padding)%} {%endfor%}{{ column.python_type.value }}),
{%- endfor %}
{%- for relationship in entity.relationships %}
{%- set padding = entity.column_length - (relationship.target_entity_name_snek_case|length) %}
        ('{{ relationship.target_entity_name_snek_case }}', {%for i in range(0, padding)%} {%endfor%}{{ relationship.target_entity_name_snek_case }}),
{%- endfor %}
    ]
)
"""

type_constructor_template = """
def create_{{ entity.class_name_snek_case }}(
{%- for column in entity.columns %}
{%- set padding = entity.column_length - (column.name|length) %}
        {{ column.name }}: {%for i in range(0, padding)%} {%endfor%}Optional[{{ column.python_type.value }}]=None,
{%- endfor %}
{%- for relationship in entity.relationships %}
{%- set padding = entity.column_length - (relationship.target_entity_name_snek_case|length) %}
        {{ relationship.target_entity_name_snek_case }}: {%for i in range(0, padding)%} {%endfor%}Optional[{{ relationship.target_entity_name }}]=None
{%- endfor %}
) -> {{ entity.class_name }}:
    return {{ entity.class_name }}(
{%- for column in entity.columns %}
{%- set padding = entity.column_length - (column.name|length) %}
        {{ column.name }}={{ column.name }} if {{ column.name }} else {{ column.default }},
{%- endfor %}
{%- for relationship in entity.relationships %}
        {{ relationship.target_entity_name_snek_case }}={{ relationship.target_entity_name_snek_case }} if {{ relationship.target_entity_name_snek_case }} else create_{{ relationship.target_entity_name_snek_case }}(), 
{%- endfor %}
    )
"""

to_type_template = """
    def to_{{ entity.class_name_snek_case }}(self) -> {{ entity.import_name }}:
        return create_{{ entity.class_name_snek_case }}(
{%- for column in entity.columns %}
            {{ column.name }}={{ column.python_type.value }}(self.{{ column.name }}),
{%- endfor %}
{%- for relationship in entity.relationships %}
            {{ relationship.target_entity_name_snek_case }}=self.{{ relationship.target_entity_name_snek_case }}.to_{{ relationship.target_entity_name_snek_case }}(), 
{%- endfor %}
        )
"""

example_entity = {
    "class_name": 'Dog',
    "columns": [
        {"name": "name", "type": "string"}, {"name": "age", "type": "int"}
    ]
}

example_from_exemplar = """
{
    "name": "Charles",
    "age": 4,
    "goodness": 11.6
}
"""

# dog_entity = _entity_from_dict(example_entity)
dog_entity = _entity_from_exemplar('Dog', json.loads(example_from_exemplar))
dog_entity.relationships = [create_relationship('Owner', True, False, JoinOption.to_one)]
print(dog_entity)

from jinja2 import Environment, BaseLoader

db_jinja_template = Environment(loader=BaseLoader).from_string(db_model_template)
db_rendered = db_jinja_template.render({"entity": dog_entity.to_dict()})
tuple_jinja_template = Environment(loader=BaseLoader).from_string(named_tuple_template)
tuple_rendered = tuple_jinja_template.render({"entity": dog_entity})
to_type_jinja_template = Environment(loader=BaseLoader).from_string(to_type_template)
to_type_rendered = to_type_jinja_template.render({"entity": dog_entity})
type_constructor_jinja_template = Environment(loader=BaseLoader).from_string(type_constructor_template)
type_constructor_rendered = type_constructor_jinja_template.render({"entity": dog_entity})
print(db_rendered)
print(to_type_rendered)
print(type_constructor_rendered)
print(tuple_rendered)
