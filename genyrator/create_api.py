import os
from enum import Enum
from typing import List, NamedTuple, Optional, Dict

import inflection

from genyrator import Entity
from genyrator.genyrator import (
    PythonTypeOption, _camel_case_to_snek_case, _snek_case_to_camel_case,
    convert_file_path_to_module_name, _type_option_to_restplus_type,
)


APIPath = NamedTuple(
    'APIPath',
    [('entity',          Entity),
     ('joined_entities', List[str]),
     ('route',           str), ]
)


class HttpVerbs(Enum):
    get =  'GET'
    post = 'POST'


def create_api_files(
        out_dir_api_endpoints: str,
        namespace:             str,
        db_models_import:      str,
        entities:              List[Entity],
        api_paths:             Optional[Dict[str, List[APIPath]]]=list(),
) -> None:
    endpoints_module = convert_file_path_to_module_name(out_dir_api_endpoints)
    try:
        os.makedirs(out_dir_api_endpoints)
    except FileExistsError:
        pass
    for entity in entities:
        with open('{}/{}'.format(out_dir_api_endpoints, '{}.py'.format(entity.class_name_snek_case)), 'w') as f:
            endpoints = render_api_endpoints(
                namespace,
                'from {} import model_to_dict'.format(endpoints_module),
                'from {} import {}'.format(endpoints_module, namespace),
                db_models_import,
                entity,
                render_restplus_model(entity, namespace)
            )
            f.write(endpoints)
            if api_paths is not None and entity.class_name_snek_case in api_paths:
                f.write(render_api_paths(namespace, api_paths[entity.class_name_snek_case]))
    with open('{}/{}'.format(out_dir_api_endpoints, '__init__.py'), 'w') as f:
        f.write(init_template.format(
            namespace="{name} = Namespace('{name}', path='/')".format(name=namespace),
        ))


def render_api_paths(namespace: str, api_paths: List[APIPath]):
    methods = []
    for path in api_paths:
        query = path.entity.class_name + ' \\\n            ' + '\n            '.join([
            '.query \\\n            '
            '.options({}) \\'.format('.'.join(["joinedload('{}')".format(je) for je in path.joined_entities])),
            '.filter_by({}_id=id) \\'.format(path.entity.class_name_snek_case),
            '.first()'
        ])
        methods.append(
            entity_to_api_get_endpoint_string(
                path.entity,
                namespace,
                path.route,
                '-'.join([_camel_case_to_snek_case(x) for x in path.joined_entities]),
                inflection.camelize('_'.join([path.entity.class_name] + path.joined_entities)),
                query,
                path.joined_entities,
            )
        )
    return '\n'.join(methods)


def render_api_endpoints(
        namespace:            str,
        namespace_import:     str,
        model_to_dict_import: str,
        db_models_import:     str,
        entity:               Entity,
        models:               str,
):
    template = """import json
from flask import request
from flask import request, Response, abort
from flask_restplus import Resource, fields
from sqlalchemy.orm import joinedload
import dateutil.parser
from werkzeug.exceptions import BadRequest
{db_models_import}
{typing_imports}
{model_to_dict_method_import}
{namespace_import}

{models}

{api_methods}
"""
    return template.format(
        db_models_import=db_models_import,
        typing_imports='from typing import Optional',
        model_to_dict_method_import=model_to_dict_import,
        api_methods='\n'.join(
            [entity_to_api_get_endpoint_string(entity, namespace), entity_to_api_post_endpoint(entity, namespace)]
        ),
        namespace_import=namespace_import,
        models=models
    )


def _create_get_by_id_method_body(
        entity_name: str,
        class_name:  str,
        query:       Optional[str]=None,
        path:        Optional[List[str]]=None
) -> str:
    query = query if query else '{class_name}.query.filter_by({entity_name}_id=id).first()'.format(
        class_name=class_name, entity_name=entity_name,
    )
    return """
        result: Optional[{class_name}] = {query}
        if result is None:
            abort(404)
        return model_to_dict(result{path})
    """.format(
        class_name=class_name, query=query, path=', ' + str(path) if path else ''
    ).lstrip()


def entity_to_api_get_endpoint_string(
        entity:        Entity,
        namespace:     str='default',
        route:         Optional[str]=None,
        endpoint:      Optional[str]=None,
        resource_name: Optional[str]=None,
        query:         Optional[str]=None,
        path:          Optional[List[str]]=None,
) -> str:
    return """@{namespace}.route('/{route}', endpoint='{endpoint_name}')
class {resource_name}(Resource):  # type: ignore{marshal_with}
    @{namespace}.doc(id='{endpoint_name}', responses={{401: 'Unauthorised', 404: 'Not Found'}})
    def get(self, id):  # type: ignore
        {body}
""".format(
        namespace=namespace,
        entity_name=entity.class_name_snek_case,
        resource_name='Get{}Resource'.format(entity.class_name) if not resource_name else resource_name,
        endpoint_name='get-{}-by-id'.format(entity.class_name_snek_case) if not endpoint else endpoint,
        route='{}/<id>'.format(entity.class_name_snek_case) if not route else route,
        body=_create_get_by_id_method_body(
            entity_name=entity.class_name_snek_case,
            class_name=entity.class_name,
            query=query,
            path=path,
        ),
        marshal_with='\n    @{}.marshal_with({}_model)'.format(namespace, entity.class_name_snek_case) if not route else ''
    )


def _create_post_by_id_method_body(entity: Entity) -> str:
    columns = []
    for c in entity.columns:
        dict_value = "data['{}']".format(c.camel_case_name)
        if c.python_type == PythonTypeOption.datetime:
            dict_value = 'dateutil.parser.parse({}) if {} else None'.format(dict_value, dict_value)
        if c.python_type == PythonTypeOption.date:
            dict_value = '{}.date'.format(dict_value)
        columns.append('{}{}={},'.format(
            ' ' * 4 * 4, c.name, dict_value
        ))

    return """    def post(self):  # type: ignore
        try:
            data = json.loads(request.data)
            db_model = {entity_class}(
{columns}
            )
            db.session.add(db_model)
            db.session.commit()
        except Exception as e:
            raise BadRequest(str(e))
        return Response(status=201)
""".format(
        entity_class=entity.class_name,
        columns='\n'.join(columns)
    )


def entity_to_api_post_endpoint(
        entity:    Entity,
        namespace: str = 'default',
) -> str:
    return """@{namespace}.route('/{entity_name}', endpoint='{endpoint_name}')
class Post{class_name}Resource(Resource):  # type: ignore
    @{namespace}.expect({model_name}, validate=False)
{body}
""".format(
        namespace=namespace,
        entity_name=entity.class_name_snek_case,
        class_name=entity.class_name,
        endpoint_name='create-{}'.format(entity.class_name_snek_case),
        body=_create_post_by_id_method_body(entity=entity),
        model_name='{}_model'.format(entity.class_name_snek_case)
    )


def entity_to_api_model_string(entity: Entity, namespace: str):
    columns = []
    for column in entity.columns:
        columns.append("'{column_name}': fields.{restplus_type}({required}),".format(
            column_name=_snek_case_to_camel_case(column.name),
            restplus_type=_type_option_to_restplus_type(column.type_option).value,
            default=column.default,
            required='required={}'.format(str(not column.nullable))
        ))
    return """
{entity_name}_model = {namespace}.model('{entity_class}', {{
    {columns}
}})
""".format(
        entity_name=entity.class_name_snek_case,
        entity_class=entity.class_name,
        columns='\n    '.join(columns),
        namespace=namespace,
    )


def render_restplus_model(entity: Entity, namespace: str) -> str:
    return entity_to_api_model_string(entity, namespace)


init_template = """import datetime
from typing import Any
import inflection
from sqlalchemy.orm.collections import InstrumentedList
from flask_restplus import Namespace


{namespace}


def model_to_dict(model, paths=list()):
    serialized_data = {{}}
    for c in model.__table__.columns:
        if c.primary_key:
            continue
        key = sqlalchemy_property_name_to_json_name(c.key)
        value = sqlalchemy_property_value_to_json_value(getattr(model, c.key))
        serialized_data[key] = value
    if not paths:
        return serialized_data
    next_path = paths.pop(0)
    next_relationship = getattr(model, next_path)
    next_key = sqlalchemy_property_name_to_json_name(next_path)
    if type(next_relationship) is InstrumentedList:
        serialized_data[next_key] = [model_to_dict(nr, paths) for nr in next_relationship]
    else:
        serialized_data[next_key] = model_to_dict(next_relationship, paths)
    return serialized_data


def sqlalchemy_property_name_to_json_name(sqlalchemy_key: str) -> str:
    return inflection.camelize(sqlalchemy_key, False)


def sqlalchemy_property_value_to_json_value(param: Any) -> str:
    property_type = type(param)
    if property_type is datetime.datetime or property_type is datetime.date:
        return param.isoformat()
    return param
"""