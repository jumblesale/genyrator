import importlib
import json
import random
import string

from behave import step, given, then, when
from typing import List, Any, Optional
from hamcrest import assert_that, equal_to, has_entry

from genyrator import (
    Entity, create_entity, Column, create_column, create_identifier_column,
    string_to_type_option,
)
from genyrator.entities.Entity import (
    string_to_operation_option, all_operations
)
from genyrator.entities.Column import IdentifierColumn
from genyrator.entities.Schema import create_schema, Schema
from test.e2e.steps.common import make_request


def _random_string(n: int) -> str:
    return ''.join(random.choices(string.ascii_letters, k=n))


def _create_test_entity(columns: List[Column], identifier_column: IdentifierColumn) -> Entity:
    return create_entity(
        class_name=_random_string(24),
        identifier_column=identifier_column,
        columns=columns,
    )


def _create_schema(context: Any, module_name: Optional[str] = None):
    entity_name = context.entity_name if hasattr(context, 'entity_name') else None
    operations = context.operations if hasattr(context, 'operations') else all_operations
    entity = create_entity(
        class_name=_random_string(36) if entity_name is None else entity_name,
        identifier_column=context.identifier_column,
        columns=context.columns,
        operations=operations,
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


@given('I have operation options "{operation}"')
def step_impl(context, operation: str):
    context.operations = set([string_to_operation_option(o) for o in operation.split(', ')])


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


@step("I import the generated app")
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
    context.response = make_request(context.client, path, method)


@when('I make a "{method}" request to "{path}" with parameters "{parameters}"')
def step_impl(context: Any, method: str, path: str, parameters: str):
    context.response = make_request(context.client, path, method, parameters)


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
    context.response = make_request(context.client, path, method, data=data)


@step('I can get entity "{path}"')
def step_impl(context, path: str):
    context.response = response = make_request(context.client, path, 'get')
    assert_that(response.status_code, equal_to(200))


@step('I cannot get entity "{path}"')
def step_impl(context, path: str):
    assert_that(make_request(context.client, path, 'get').status_code, equal_to(404))


@step("that response matches the original data")
def step_impl(context):
    response_data = context.response.json
    original_data = context.data
    assert_that(response_data, equal_to(original_data))


@step('the response has "{field}" with value "{value}"')
def response_has_field_value(context, field: str, value: Any):
    assert_that(json.loads(context.response.data), has_entry(field, value))


@step('I load data for "{entity_name}"')
def step_impl(context, entity_name):
    db = context.generated_module.db
    model_module = importlib.import_module(
        '.'.join([context.module_name, 'sqlalchemy', 'model', entity_name])
    )
    constructor = getattr(model_module, entity_name)
    args = {}
    for row in context.table:
        args[row['name']] = row['value']
    args['id'] = None
    model = constructor(**args)
    with context.app.app_context():
        db.session.add(model)
        db.session.commit()


@step('making "{operations_list}" requests to "{endpoint}" gives http status "{status}"')
def step_impl(context, operations_list: str, endpoint: str, status: int):
    for operation in operations_list.split(','):
        response = make_request(
            client=context.client,
            endpoint=endpoint,
            method=operation,
        )
        assert_that(response.status_code, equal_to(int(status)), f'{operation}')


@step("I create an example app")
def step_impl(context):
        context.execute_steps("""
        Given I have an entity "ExampleEntity" with properties
          | name      | type |
          | test_name | str  |
          And identifier column "test_id" with type "int"
          And I create a schema from those entities
          And the app is running
          And I load data for "ExampleEntity"
          | name      | value |
          | test_name | test  |
          | test_id   | 3     |
    """)


@when('I create a fixture for the "{entity_name}" entity with values')
def step_impl(context, entity_name: str):
    fixture_module_name = f'{context.module_name}.sqlalchemy.fixture.{entity_name}'
    fixture_module = importlib.import_module(fixture_module_name)
    fixture = getattr(fixture_module, f'{entity_name}Factory')
    args = json.loads(context.text)
    with context.app.app_context():
        fixture.create(**args)
        context.generated_module.db.session.commit()


@then('the db contains "{count}" "{model_name}" entity')
def step_impl(context, count: str, model_name: str):
    model_module_name = f'{context.module_name}.sqlalchemy.model.{model_name}'
    model_module = importlib.import_module(model_module_name)
    model = getattr(model_module, model_name)
    with context.app.app_context():
        result = model.query.all()
        assert_that(len(result), equal_to(int(count)))
