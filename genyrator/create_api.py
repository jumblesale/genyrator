import os
from enum import Enum
from typing import List, NamedTuple, Optional
from genyrator import Entity
from genyrator.genyrator import (
    TypeOption, PythonTypeOption, _camel_case_to_snek_case, _snek_case_to_camel_case,
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
        out_dir_api_endpoints:       str,
        namespace:                   str,
        model_to_dict_method_import: str,
        db_models_import:            str,
        entities:                    List[Entity],
        api_paths:                   Optional[List[APIPath]]=list(),
) -> None:
    try:
        os.makedirs(out_dir_api_endpoints)
    except FileExistsError:
        pass
    with open('{}/{}'.format(out_dir_api_endpoints, 'endpoints.py'), 'w') as f:
        f.write(
            render_api_endpoints(namespace, model_to_dict_method_import, db_models_import, entities)
        )
        if api_paths is not None:
            f.write(render_api_paths(namespace, api_paths))


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
                _snek_case_to_camel_case(''.join(path.joined_entities)),
                query,
                path.joined_entities,
            )
        )
    return '\n'.join(methods)


def render_api_endpoints(
        namespace:                   str,
        model_to_dict_method_import: str,
        db_models_import:            str,
        entities:                    List[Entity],
):
    template = """import json
from flask import request
from flask import request, Response, abort
from flask_restplus import Namespace, Resource
from sqlalchemy.orm import joinedload
import dateutil.parser
{db_models_import}
{typing_imports}
{model_to_dict_method_import}


{namespace}


{api_methods}
""".format(
        db_models_import=db_models_import,
        typing_imports='from typing import Optional',
        model_to_dict_method_import=model_to_dict_method_import,
        api_methods='\n'.join(
            ['\n'.join([entity_to_api_get_endpoint_string(e, namespace), entity_to_api_post_endpoint(e, namespace)])
             for e in entities]
        ),
        namespace="{name} = Namespace('{name}', path='/')".format(name=namespace)
    )
    return template


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
        return Response(
            response=json.dumps(model_to_dict(result{path})),
            status=200,
            mimetype='application/json'
        )
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
class {resource_name}(Resource):  # type: ignore
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
    )


def _create_post_by_id_method_body(entity: Entity) -> str:
    columns = []
    for c in entity.columns:
        dict_value = "data['{}']".format(c.camel_case_name)
        if c.python_type == PythonTypeOption.datetime:
            dict_value = 'dateutil.parser.parse({})'.format(dict_value)
        if c.python_type == PythonTypeOption.date:
            dict_value = '{}.date'.format(dict_value)
        columns.append('{}{}={},'.format(
            ' ' * 4 * 3, c.name, dict_value
        ))

    return """    def post(self):  # type: ignore
        data = json.loads(request.data)
        db_model = {entity_class}(
{columns}
        )
        db.session.add(db_model)
        db.session.commit()
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
{body}
""".format(
        namespace=namespace,
        entity_name=entity.class_name_snek_case,
        class_name=entity.class_name,
        endpoint_name='create-{}'.format(entity.class_name_snek_case),
        body=_create_post_by_id_method_body(entity=entity),
    )
