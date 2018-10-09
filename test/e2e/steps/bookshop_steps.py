import datetime
import uuid
from typing import Mapping, cast, MutableMapping
import json

from behave import given, when, then
from hamcrest import assert_that, equal_to, instance_of, none

from test.e2e.steps.common import make_request
from bookshop.sqlalchemy.model.Author import Author
from bookshop.sqlalchemy.model.Book import Book


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


@step("I put a book entity with a relationship to that author")
def step_impl(context):
    book = generate_example_book()
    context.created_book = book = {
        **book,
        **{'authorId': context.author_entity['id']}
    }
    response = make_request(client=context.client, endpoint=f'book/{book["id"]}',
                            method='put', data=book)
    assert_that(response.status_code, equal_to(201))


@step("I also put a collaborator relationship to that author")
def step_impl(context):
    context.created_book['collaboratorId'] = context.author_entity['id']
    book = context.created_book
    response = make_request(client=context.client, endpoint=f'book/{book["id"]}',
                            method='put', data=book)
    assert_that(response.status_code, equal_to(201))


@when("I get that book entity")
def step_impl(context):
    book = context.created_book
    url = f'/book/{book["id"]}'
    response = make_request(client=context.client, endpoint=url, method='get')
    assert_that(response.status_code, equal_to(200))
    data = json.loads(response.data)
    context.retrieved_book = data


@step("I can see that author in the response")
def step_impl(context):
    author = context.retrieved_book['author']
    assert_that(author['id'], equal_to(context.author_entity['id']))


@when('I get that "{entity_name}" SQLAlchemy model')
def step_impl(context, entity_name: str):
    from bookshop import app
    context.app_context = app.app_context()
    context.app_context.push()
    if entity_name == 'author':
        model = Author
        filter_ = Author.author_id == context.author_entity['id']
    elif entity_name == 'book':
        model = Book
        filter_ = Book.book_id == context.created_book['id']
    else:
        raise Exception('Only supports books and authors')

    setattr(
        context,
        f'sql_{entity_name}',
        getattr(model, 'query').filter(filter_).one()
    )


@then('"{target}" should have "2" items in it')
def step_impl(context, target):
    length = len(_extract_target(context, target))
    assert_that(length, equal_to(2))
    context.app_context.pop()


@then('"{target}" should be that author')
def step_impl(context, target):
    author = Author.query.filter(Author.author_id == context.author_entity['id']).one()
    assert_that(_extract_target(context, target), equal_to(author))


@then('"{target}" should be None')
def step_impl(context, target):
    assert_that(_extract_target(context, target), none())


def _extract_target(context, target):
    if isinstance(target, str):
        target = target.split('.')
    if len(target) == 0:
        return context
    else:
        return _extract_target(getattr(context, target[0]), target[1:])
