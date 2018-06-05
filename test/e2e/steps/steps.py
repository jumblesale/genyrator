import importlib
import random
import string
from behave import *
from typing import List, Any

from genyrator import (
    Entity, create_entity, Column, create_column, create_identifier_column, string_to_type_option,
)
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


@given("I have an entity with properties")
def step_impl(context: Any):
    columns = []
    for row in context.table:
        columns.append(create_column(
            row['name'], string_to_type_option(row['type'])
        ))
    context.columns = columns


@step('identifier column "{name}" with type "{column_type}"')
def step_impl(context: Any, name: str, column_type: str):
    context.identifier_column = create_identifier_column(
        name, string_to_type_option(column_type),
    )


@step("I create a schema from those entities")
def step_impl(context: Any):
    entity = create_entity(
        class_name=_random_string(36),
        identifier_column=context.identifier_column,
        columns=context.columns,
    )
    module_name = _random_string(14)
    schema = create_schema(
        module_name='output.{}'.format(module_name),
        entities=[entity],
        file_path=['output', module_name],
    )
    context.schema = schema
    context.module_name = 'output.{}'.format(module_name)
    context.module_path = 'output/{}'.format(module_name)


@step("I write that schema")
def step_impl(context: Any):
    schema: Schema = context.schema
    schema.write_files()


@then("I can import the generated app")
def step_impl(context):
    generated_module = importlib.import_module(context.module_name)
    context.app = generated_module.app


@step("I can run the generated app")
def step_impl(context):
    app = context.app
    app.testing = True
    context.client = client = app.test_client()
    print(client.get('/'))
