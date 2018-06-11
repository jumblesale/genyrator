import importlib
import json
import random
import string
from functools import partial

from behave import *
from typing import List, Any, Dict, Optional

from flask.testing import FlaskClient
from hamcrest import assert_that, equal_to

from genyrator import (
    Entity, create_entity, Column, create_column, create_identifier_column,
    string_to_type_option,
)
from genyrator.entities.Entity import all_operations as all_entity_operations
from genyrator.entities.Column import IdentifierColumn
from genyrator.entities.Schema import create_schema, Schema


def _random_string(n: int) -> str:
    return ''.join(random.choices(string.ascii_letters, k=n))


def _create_test_entity(columns: List[Column], identifier_column: IdentifierColumn) -> Entity:
    return create_entity(
        class_name=_random_string(24),
        identifier_column=identifier_column,
        columns=columns,
    )


def _make_request(client: FlaskClient, endpoint: str, method: str, parameters: Optional[str]=None, data: Optional[Dict]=None):
    if parameters is not None:
        parameters = '&'.join(parameters.split(','))
        endpoint = '?'.join([endpoint, parameters])
    method = partial(getattr(client, method.lower()), endpoint)
    if data is not None:
        return method(data=json.dumps(data), content_type='application/json')
    return method()


def _create_schema(context: Any, module_name: Optional[str]=None):
    entity = create_entity(
        class_name=_random_string(36) if not context.entity_name else context.entity_name,
        identifier_column=context.identifier_column,
        columns=context.columns, operations=all_entity_operations,
    )
    module_name = _random_string(14) if module_name is None else module_name
    schema = create_schema(
        module_name='output.{}'.format(module_name),
        entities=[entity],
        file_path=['output', module_name],
    )
    context.schema = schema
    context.module_name = 'output.{}'.format(module_name)
    context.module_path = 'output/{}'.format(module_name)


@given('I have an entity "{name}" with properties')
def step_impl(context: Any, name: str):
    context.entity_name = name
    entity_with_properties(context)


@given("I have an entity with properties")
def entity_with_properties(context: Any):
    columns = []
    for row in context.table:
        if 'nullable' in row.headings:
            nullable = row['nullable'] == 'True'
        else:
            nullable = False
        columns.append(create_column(
            row['name'], string_to_type_option(row['type']), nullable=nullable
        ))
    context.columns = columns


@step('identifier column "{name}" with type "{column_type}"')
def step_impl(context: Any, name: str, column_type: str):
    context.identifier_column = create_identifier_column(
        name, string_to_type_option(column_type),
    )


@step("I create a schema from those entities")
def step_impl(context: Any):
    _create_schema(context)


@step('I create a schema "{schema_name}" from those entities')
def step_impl(context: Any, schema_name: str):
    _create_schema(context, schema_name)


@step("I write that schema")
def write_schema(context: Any):
    schema: Schema = context.schema
    schema.write_files()


@then("I can import the generated app")
def import_app(context):
    context.generated_module = generated_module = importlib.import_module(context.module_name)
    context.app = generated_module.app


@step("I initialize the database")
def init_db(context):
    db = context.generated_module.db
    with context.app.app_context():
        db.drop_all()
        db.create_all()


@step("I can run the generated app")
def run_app(context):
    app = context.app
    app.testing = True
    context.client = client = app.test_client()
    response = client.get('/')
    assert_that(response.status_code, equal_to(200))


@step("the app is running")
def app_is_running(context: Any):
    write_schema(context)
    import_app(context)
    init_db(context)
    run_app(context)


@step('I make a "{method}" request to "{path}"')
def step_impl(context, method: str, path: str):
    context.response = _make_request(context.client, path, method)


@when('I make a "{method}" request to "{path}" with parameters "{parameters}"')
def step_impl(context: Any, method: str, path: str, parameters: str):
    context.response = _make_request(context.client, path, method, parameters)


@then('I get http status "{status}"')
def step_impl(context: Any, status: int):
    assert_that(context.response.status_code, equal_to(int(status)))


@given("I have text data")
def step_impl(context):
    context.data = context.text


@step("I have json data")
def have_json_data(context):
    context.data = json.loads(context.text)


@step('I make a "{method}" request to "{path}" with that json data')
def step_impl(context: Any, method: str, path: str):
    data = context.data
    context.response = _make_request(context.client, path, method, data=data)


@step('I can get entity "{path}"')
def step_impl(context, path: str):
    context.response = response = _make_request(context.client, path, 'get')
    assert_that(response.status_code, equal_to(200))


@step('I cannot get entity "{path}"')
def step_impl(context, path: str):
    assert_that(_make_request(context.client, path, 'get').status_code, equal_to(404))


@step("that response matches the original data")
def step_impl(context):
    assert_that(json.loads(context.response.data), equal_to(context.data))
