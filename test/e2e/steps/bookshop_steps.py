import datetime
import uuid
from typing import Mapping
import json

from behave import given, when, then
from hamcrest import assert_that, equal_to

from test.e2e.steps.common import make_request


def generate_example_book() -> Mapping[str, str]:
    return {"id": str(uuid.uuid4()), "name": "the outsider", "rating": 4.96, "published": "1967-04-24",
            "created": str(datetime.datetime.now())}


def generate_example_genre() -> Mapping[str, str]:
    return {"id": str(uuid.uuid4()), "title": "fiction"}


def generate_example_book_genre(book_uuid: str, genre_uuid: str) -> Mapping[str, str]:
    return {"id": str(uuid.uuid4()), "bookId": book_uuid, "genreId": genre_uuid}


def generate_example_author() -> Mapping[str, str]:
    return {"id": str(uuid.uuid4()), "name": 'camus'}


example_entity_generators = {
    'book':   generate_example_book,
    'genre':  generate_example_genre,
    'author': generate_example_author,
}


@given('I have the example "{app_name}" application')
def step_impl(context, app_name: str):
    from bookshop import app, db
    client = context.client = app.test_client()
    with app.app_context():
        db.drop_all()
        db.create_all()
    assert_that(client.get('/').status_code, equal_to(200))


@given('I put an example "{entity_name}" entity')
def step_impl(context, entity_name: str):
    entity = example_entity_generators[entity_name]()
    entity_id = entity['id']
    setattr(context, f'{entity_name}_entity', entity)
    response = make_request(
        client=context.client, endpoint=f"{entity_name}/{entity_id}",
        method='put', data=entity
    )
    assert_that(response.status_code, equal_to(201))


@when('I put a "book_genre" join entity')
def step_impl(context):
    book_uuid =  context.book_entity['id']
    genre_uuid = context.genre_entity['id']
    book_genre_entity = generate_example_book_genre(
        book_uuid=book_uuid, genre_uuid=genre_uuid,
    )
    context.book_genre_uuid = book_genre_uuid = book_genre_entity['id']
    response = make_request(client=context.client, endpoint=f'book-genre/{book_genre_uuid}',
                            method='put', data=book_genre_entity)
    assert_that(response.status_code, equal_to(201))


@then('I can see that genre in the response from "{url}"')
def step_impl(context, url: str):
    url = url.replace('{id}', context.book_entity['id'])
    response = make_request(client=context.client, endpoint=url, method='get')
    assert_that(response.status_code, equal_to(200))
    data = json.loads(response.data)
    genre = data['genre']
    assert_that(genre['id'], equal_to(context.genre_entity['id']))


@when('I patch that "{entity_name}" entity with that "{entity_id}" id')
def step_impl(context, entity_name: str, entity_id: str):
    patch_id = getattr(context, f'{entity_id}_entity')['id']
    existing_entity_id = getattr(context, f'{entity_name}_entity')['id']
    data = {
        f"{entity_id}Id": patch_id,
    }
    response = make_request(client=context.client, endpoint=f'{entity_name}/{existing_entity_id}',
                            method='patch', data=data)
    assert_that(response.status_code, equal_to(200))


@then('I can see that book in the response from "{url}"')
def step_impl(context, url: str):
    url = url.replace('{id}', context.author_entity['id'])
    response = make_request(client=context.client, endpoint=url, method='get')
    assert_that(response.status_code, equal_to(200))
    data = json.loads(response.data)
    ...


@given('I put an incorrect "book_genre" join entity')
def step_impl(context):
    book_genre_entity = generate_example_book_genre(
        book_uuid=str(uuid.uuid4()), genre_uuid=str(uuid.uuid4()),
    )
    context.book_genre_uuid = book_genre_uuid = book_genre_entity['id']
    response = make_request(client=context.client, endpoint=f'book-genre/{book_genre_uuid}',
                            method='put', data=book_genre_entity)
    context.response = response


@then("I get http status 400")
def step_impl(context):
    assert_that(context.response.status_code, equal_to(400))