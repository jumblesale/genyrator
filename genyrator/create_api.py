import os
from enum import Enum
from typing import List
from genyrator import Entity
from genyrator.genyrator import TypeOption, PythonTypeOption


class HttpVerbs(Enum):
    get =  'GET'
    post = 'POST'


def create_api_files(
        out_dir_api_endpoints:       str,
        namespace:                   str,
        model_to_dict_method_import: str,
        db_models_import:            str,
        entities:                    List[Entity],
) -> None:
    try:
        os.makedirs(out_dir_api_endpoints)
    except FileExistsError:
        pass
    with open('{}/{}'.format(out_dir_api_endpoints, 'endpoints.py'), 'w') as f:
        f.write(
            render_api_endpoints(namespace, model_to_dict_method_import, db_models_import, entities)
        )


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


def _create_get_by_id_method_body(entity_name: str, class_name: str) -> str:
    return """
        result: Optional[{class_name}] = {class_name}.query.filter_by({entity_name}_id=id).first()
        if result is None:
            abort(404)
        return Response(
            response=json.dumps(model_to_dict(result)),
            status=200,
            mimetype='application/json'
        )
    """.format(class_name=class_name, entity_name=entity_name).lstrip()


def entity_to_api_get_endpoint_string(
        entity:    Entity,
        namespace: str='default',
) -> str:
    return """@{namespace}.route('/{entity_name}/<id>', endpoint='{endpoint_name}')
class Get{class_name}Resource(Resource):  # type: ignore
    @{namespace}.doc(id='{endpoint_name}', responses={{401: 'Unauthorised', 404: 'Not Found'}})
    def get(self, id):  # type: ignore
        {body}
""".format(
        namespace=namespace,
        entity_name=entity.class_name_snek_case,
        class_name=entity.class_name,
        endpoint_name='get-{}-by-id'.format(entity.class_name_snek_case),
        body=_create_get_by_id_method_body(
            entity_name=entity.class_name_snek_case,
            class_name=entity.class_name,
        ),
    )


def _create_post_by_id_method_body(entity: Entity) -> str:
    columns = []
    for c in entity.columns:
        dict_value = "row['{}']".format(c.camel_case_name)
        if c.python_type == PythonTypeOption.datetime:
            dict_value = 'dateutil.parser.parse({})'.format(dict_value)
        if c.python_type == PythonTypeOption.date:
            dict_value = '{}.date'.format(dict_value)
        columns.append('{}{}={},'.format(
            ' ' * 4 * 4, c.name, dict_value
        ))

    return """    def post(self):  # type: ignore
        data = json.loads(request.data)
        for row in data:
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
