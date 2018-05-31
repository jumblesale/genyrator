import os
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
    bool =     'bool'
    dict =     'dict'
    list =     'list'
    datetime = 'datetime'
    date =     'date'


def _string_to_type_option(string_type: str) -> TypeOption:
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


def _type_option_to_sqlalchemy_type(type_option: TypeOption) -> SqlAlchemyTypeOption:
    return {
        TypeOption.string:   SqlAlchemyTypeOption.string,
        TypeOption.int:      SqlAlchemyTypeOption.int,
        TypeOption.float:    SqlAlchemyTypeOption.float,
        TypeOption.bool:     SqlAlchemyTypeOption.bool,
        TypeOption.datetime: SqlAlchemyTypeOption.datetime,
        TypeOption.date:     SqlAlchemyTypeOption.date,
    }[type_option]


def _type_option_to_restplus_type(type_option: TypeOption) -> RestplusTypeOption:
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


def _type_option_to_python_type(type_option: TypeOption) -> PythonTypeOption:
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


def _type_option_to_default_value(type_option: TypeOption) -> str:
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
    type_option:     TypeOption =           attr.ib()
    nullable:        bool =                 attr.ib()

    def to_dict(self) -> Dict:
        return self.__dict__

    def to_sqlalchemy_model_string(self, padding: int, foreign_key_relationship: Optional[str] = None) -> str:
        if foreign_key_relationship is not None:
            foreign_key = ", db.ForeignKey('{relationship}')".format(relationship=foreign_key_relationship)
        else:
            foreign_key = ''
        return '{column_name} ={spacing} db.Column(db.{sql_type}{fk}{index}{nullable})'.format(
            column_name=self.name, sql_type=self.sqlalchemy_type.value,
            spacing=_create_padding(padding, self.name), fk=foreign_key,
            index=', index=True' if self.index else '',
            nullable=', nullable=True' if self.nullable is True else '',
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
        if self.python_type == PythonTypeOption.datetime:
            type = ''
        else:
            type = self.python_type.value
        return '{name}={type}(self.{name}),'.format(
            name=self.name, type=type,
        )

    def to_named_tuple_string(self, padding: int):
        return "        ('{name}', {spacing}{type}),".format(
            name=self.name, spacing=_create_padding(padding, self.name),
            type=self.python_type.value,
        )

    def to_create_json_string(self, padding: int, entity_name: str) -> str:
        return '        "{key}": {spacing}{entity_name}.{key}'.format(
            spacing=_create_padding(padding, self.name),
            key=self.name,
            entity_name=entity_name,
        )


@attr.s
class ForeignKey(Column):
    relationship: str = attr.ib()

    def to_sqlalchemy_model_string(self, padding: int, foreign_key_relationship: Optional[str] = None):
        return super().to_sqlalchemy_model_string(padding, self.relationship)


def create_column(
        name:                     str,
        type_option:              TypeOption,
        foreign_key_relationship: Optional[str]=None,
        index:                    bool=False,
        nullable:                 bool=True,
) -> Column:
    constructor = Column if foreign_key_relationship is None else ForeignKey
    args = {
        "name":            _camel_case_to_snek_case(name),
        "camel_case_name": _snek_case_to_camel_case(name),
        "type_option":     type_option,
        "sqlalchemy_type": _type_option_to_sqlalchemy_type(type_option),
        "python_type":     _type_option_to_python_type(type_option),
        "default":         _type_option_to_default_value(type_option),
        "index":           index,
        "nullable":        nullable,
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
        if self.join == JoinOption.to_one:
            type = "Optional['{}']".format(self.target_entity_name)
        else:
            type = "List[Optional['{}']]".format(self.target_entity_name)
        return '{name}: {spacing}{type}=None,'.format(
            name=self.target_entity_name_snek_case, spacing=_create_padding(padding, self.target_entity_name_snek_case),
            type=type
        )

    def to_type_constructor_body_string(self) -> str:
        return '{name}={name} if {name} else {default},'.format(
            name=self.target_entity_name_snek_case,
            default='None',
        )

    def to_sqlalchemy_type_constructor_string(self, entity_name: str) -> str:
        to_type_method = 'to_{}({}=True)'.format(
            _camel_case_to_snek_case(self.target_entity_name),
            entity_name,
        )
        constructor = 'self.{name}.{to_type} if self.{name} and not {arg_name} else None'.format(
            name=self.target_entity_name_snek_case,
            to_type=to_type_method,
            arg_name=_camel_case_to_snek_case(self.target_entity_name),
        )
        if self.join == JoinOption.to_one:
            method = constructor
        else:
            method = '[x.{} for x in self.{}] if self.{} is not None and not {} else []'.format(
                to_type_method,
                self.target_entity_name_snek_case,
                self.target_entity_name_snek_case,
                _camel_case_to_snek_case(self.target_entity_name),
            )
        return '            {name}={method},'.format(
            name=self.target_entity_name_snek_case,
            method=method,
        )

    def to_sqlalchemy_model_string(self, padding: int) -> str:
        template = "    {name} = {spacing}db.relationship('{class_name}', lazy={lazy}, uselist={uselist}{secondary})".format(
            name=self.target_entity_name_snek_case,
            class_name=self.target_entity_name,
            uselist=str(self.join == JoinOption.to_many),
            spacing=_create_padding(padding, self.target_entity_name_snek_case),
            lazy=str(self.lazy),
            secondary=", secondary='{}'".format(self.join_table),
        )
        return template

    def to_named_tuple_string(self, padding: int):
        return "        ('{name}', {spacing}{type}),".format(
            name=self.target_entity_name_snek_case,
            spacing=_create_padding(padding, self.target_entity_name_snek_case),
            type='Any'
        )


def create_relationship(
        target_entity_class_name: str,
        nullable:                 bool,
        lazy:                     bool,
        join:                     JoinOption,
        join_table:               Optional[str]=None,
        property_name:            Optional[str]=None,
) -> Relationship:
    target_entity_name_snek_case = _camel_case_to_snek_case(target_entity_class_name)
    return Relationship(
        target_entity_name=target_entity_class_name,
        target_entity_name_snek_case=property_name if property_name else target_entity_name_snek_case,
        nullable=nullable,
        lazy=lazy,
        join=join,
        join_table=str(join_table) if join_table else None,
    )


@attr.s
class Entity(object):
    class_name:           str =                attr.ib()
    columns:              List[Column] =       attr.ib()
    class_name_snek_case: str =                attr.ib()
    import_name:          str =                attr.ib()
    column_length:        int =                attr.ib()
    relationships:        List[Relationship] = attr.ib()
    table_name:           Optional[str] =      attr.ib()
    uniques:              List[List[str]] =    attr.ib()
    table_args:           Optional[str] =      attr.ib()

    def to_dict(self) -> Dict:
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
class {class_name}(db.Model):  # type: ignore{table_name}
    id ={spacing}db.Column(db.Integer, primary_key=True)
    {properties}{table_args}"""

        columns = '\n    '.join(
            [c.to_sqlalchemy_model_string(self.column_length) for c in self.columns]
        ),
        relationships = '\n'.join(
            [r.to_sqlalchemy_model_string(self.column_length) for r in self.relationships]
        ),
        return template.format(
            class_name=self.class_name,
            spacing=' ' * (self.column_length - 1),
            properties='\n'.join(columns + relationships),
            type_constructor=self.to_sqlalchemy_type_constructor(),
            table_name="\n    __tablename__ = '{}'\n".format(self.table_name) if self.table_name else '',
            table_args='\n    __table_args__ = {}{}'.format(
                _create_padding(self.column_length, '__table_args__'), self.table_args
            ) if self.table_args else '',
        )

    def to_sqlalchemy_type_constructor(self) -> str:
        template =\
            """
    def to_{class_name}(self{args}) -> {import_name}:
        return create_{class_name}(
            {properties}
        )
"""
        tab = ' ' * 4
        columns = ('\n' + tab * 3).join(
            [c.to_sqlalchemy_type_constructor_string() for c in self.columns]
        ),
        relationships = '\n'.join(
            [r.to_sqlalchemy_type_constructor_string(_camel_case_to_snek_case(self.class_name)) for r in self.relationships]
        ),
        args = ', '.join([
            _camel_case_to_snek_case(r.target_entity_name) + '=False' for r in self.relationships
        ]) + ', **kwargs'
        return template.format(
            class_name=self.class_name_snek_case,
            import_name=self.import_name,
            properties='\n'.join(columns + relationships).rstrip(),
            args=', ' + args if args else ''
        )

    def to_type_string(self) -> str:
        properties_join = '\n'
        columns = properties_join.join([c.to_named_tuple_string(self.column_length) for c in self.columns])
        relationships = properties_join.join(
            [r.to_named_tuple_string(self.column_length) for r in self.relationships]
        ) + '\n'
        return "{class_name} = NamedTuple(\n    '{class_name}', [\n{columns}\n{relationships}    ]\n)".format(
            class_name=self.class_name, columns=columns, relationships=relationships,
        )

    def to_create_json_string(self) -> str:
        signature = 'def {name}_to_json({name}: {type}):\n    return {{'.format(
            name=self.class_name_snek_case, type=self.class_name
        )
        column_body = '\n'.join(
            [c.to_create_json_string(self.column_length, self.class_name_snek_case) for c in self.columns]
        )
        return '\n'.join([signature, column_body, '    }'])


def add_relationship_to_entity(relationship: Relationship, entity: Entity):
    return create_entity(
        entity.class_name, entity.columns, entity.relationships + [relationship],
        entity.table_name, entity.uniques,
    )


def _camel_case_to_snek_case(x: str) -> str:
    return inflection.underscore(x)


def _snek_case_to_camel_case(x: str) -> str:
    return inflection.camelize(x, False)


def _entity_name_to_file_name(entity: Entity):
    return '{}.py'.format(entity.class_name_snek_case)


def create_entity(
        class_name:    str,
        columns:       List[Column],
        relationships: List[Relationship] = list(),
        table_name:    Optional[str]=None,
        uniques:       List[List[str]]=list(),
) -> Entity:
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
        table_name=table_name if table_name else None,
        uniques=uniques,
        table_args='({}, )'.format(', '.join(
            ['UniqueConstraint({})'.format(', '.join(
                ["'{}'".format(_camel_case_to_snek_case(column)) for column in uc]
            )) for uc in uniques])) if uniques else None
    )


def create_entity_from_exemplar(
        class_name:    str,
        exemplar:      Dict,
        foreign_keys:  List[Tuple[str, str]]=list(),
        indexes:       List[str]=list(),
        relationships: Optional[List[Relationship]] = list(),
        table_name:    Optional[str]=None,
        uniques:       Optional[List[List[str]]]=list()
) -> Entity:
    columns = []
    foreign_keys_dict = {}
    for fk_key, fk_value in foreign_keys:
        foreign_keys_dict[fk_key] = '{table}.{fk_column}'.format(
            table=fk_value, fk_column=_camel_case_to_snek_case(fk_key)
        )
    for k, v in exemplar.items():
        if v is None:
            v = ''
        type_name = type(v).__name__
        type_option = _string_to_type_option(type_name)
        if type_option == TypeOption.string and _is_string_date_time_ish(v):
            type_option = TypeOption.datetime
        foreign_key = foreign_keys_dict[k] if k in foreign_keys_dict else None
        index = k in indexes
        columns.append(
            create_column(k, type_option, foreign_key, index)
        )
    return create_entity(
        class_name=class_name,
        columns=columns,
        relationships=relationships,
        table_name=table_name,
        uniques=uniques,
    )


def create_entity_from_type_dict(
        class_name:    str,
        type_dict:     Dict,
        foreign_keys:  List[Tuple[str, str]]=list(),
        indexes:       List[str]=list(),
        relationships: Optional[List[Relationship]] = list(),
        table_name:    Optional[str]=None,
        uniques:       Optional[List[List[str]]]=list()
) -> Entity:
    columns = []
    foreign_keys_dict = {}
    for fk_key, fk_value in foreign_keys:
        foreign_keys_dict[fk_key] = '{table}.{fk_column}'.format(
            table=fk_value, fk_column=_camel_case_to_snek_case(fk_key)
        )
    for k, v in type_dict.items():
        type_option = _string_to_type_option(v)
        foreign_key = foreign_keys_dict[k] if k in foreign_keys_dict else None
        index = k in indexes
        columns.append(
            create_column(k, type_option, foreign_key, index)
        )
    return create_entity(
        class_name=class_name,
        columns=columns,
        relationships=relationships,
        table_name=table_name,
        uniques=uniques,
    )


def render_db_model(entity: Entity, db_import: str):
    return '{db_import}\n{datetime_imports}\n{sqlalchemy_imports}\n\n{entity}'.format(
        db_import=db_import,
        entity=entity.to_sqlalchemy_model(),
        datetime_imports='from datetime import datetime',
        sqlalchemy_imports='from sqlalchemy import UniqueConstraint'
    )


def render_type_model(entity: Entity, parent_module: str, types_path: str):
    relationship_imports = '\n'.join(['from {types_path}.{entity_name} import {class_name}, create_{entity_name}'.format(
        class_name=r.target_entity_name,
        entity_name=r.target_entity_name_snek_case,
        types_path='{}.{}'.format(parent_module, convert_file_path_to_module_name(types_path))
    ) for r in entity.relationships])
    return """{named_tuple}

{tuple_constructor}""".format(
        named_tuple=entity.to_type_string(),
        tuple_constructor=entity.to_type_constructor_string(),
        relationship_imports=relationship_imports,
    )


def render_type_constructor(entity: Entity):
    return entity.to_type_constructor_string()


def convert_file_path_to_module_name(file_path: str) -> str:
    return file_path.replace(os.sep, '.')


def create_entity_files(
        out_dir_db_models: str,
        out_dir_types:     str,
        db_import:         str,
        parent_module:     str,
        entities:          List[Entity],
    ) -> None:
    for directory in ['{}/{}'.format(parent_module, target_dir) for target_dir in [out_dir_db_models, out_dir_types]]:
        try:
            os.makedirs(directory)
        except FileExistsError:
            continue
    datetime_imports = 'from datetime import datetime'
    with open('{}/{}/{}'.format(parent_module, out_dir_types, '__init__.py'), 'w') as type_init_file:
        type_init_file.write("""from typing import NamedTuple, Optional, Any, List
{datetime_imports}
""".format(datetime_imports=datetime_imports,))
    with open('{}/{}/{}'.format(parent_module, out_dir_types, '__init__.py'), 'a') as type_init_file:
        for entity in entities:
            file_name = _entity_name_to_file_name(entity)
            db_model = render_db_model(entity=entity, db_import=db_import)
            with open('{}/{}/{}'.format(parent_module, out_dir_db_models, file_name), 'w') as db_model_file:
                db_model_file.write(db_model)
            type_model = render_type_model(entity, parent_module=parent_module, types_path=out_dir_types)
            type_init_file.write('\n\n' + type_model)

    with open('{}/{}/{}'.format(parent_module, out_dir_db_models, '__init__.py'), 'w') as f:
        for entity in entities:  # type: Entity
            import_template = """
from {parent}.{module_path}.{module_name} import {model_name}\n""".format(
                parent=parent_module,
                module_path=convert_file_path_to_module_name(out_dir_db_models),
                module_name=entity.class_name_snek_case,
                model_name=entity.class_name,
            ).lstrip()
            f.write(import_template)
