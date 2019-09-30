# flake8: noqa
import datetime
import uuid
from typing import Mapping, cast, MutableMapping
import json

from behave import given, when, then
from hamcrest import assert_that, equal_to, instance_of, none, less_than, is_not

from test.e2e.steps.common import make_request
from bookshop.sqlalchemy.model.Author import Author
from bookshop.sqlalchemy.model.Book import Book


def generate_example_book() -> Mapping[str, str]:
    return {"id": str(uuid.uuid4()), "name": "the outsider", "rating": 4.96, "published": "1967-04-24"}


def generate_example_genre() -> Mapping[str, str]:
    return {"id": str(uuid.uuid4()), "title": "fiction"}


def generate_example_book_genre(book_uuid: str, genre_uuid: str) -> Mapping[str, str]:
    return {"id": str(uuid.uuid4()), "bookId": book_uuid, "genreId": genre_uuid}


def generate_example_author() -> Mapping[str, str]:
    return {"id": str(uuid.uuid4()), "name": 'camus'}


def generate_example_related_book() -> Mapping[str, str]:
    return {"id": str(uuid.uuid4())}


example_entity_generators = {
    'book':   generate_example_book,
    'genre':  generate_example_genre,
    'author': generate_example_author,
    'related-book': generate_example_related_book,
}


@given('I have the example "{app_name}" application')
def step_impl(context, app_name: str):
    from bookshop import app, db
    client = context.client = app.test_client()
    with app.app_context():
        db.drop_all()
        db.create_all()
    assert_that(client.get('/').status_code, equal_to(200))


@given('I put an example "{entity_type}" entity')
def step_impl(context, entity_type: str):
    _put_entity(context, entity_type, f'{entity_type}_entity', {})


@given('I put an example set of books')
def step_impl(context):
    _put_entity(context, 'book', 'book1', {'name': 'Wind in the Willows', 'rating': 3.2})
    _put_entity(context, 'book', 'book2', {'name': 'Jungle Book', 'rating': 4.6})
    _put_entity(context, 'book', 'book3', {'name': 'Peter Rabbit', 'rating': 3.2})


@given('I put an example "{entity_type}" entity called "{entity_name}" with a "favouriteAuthorId" from "{target_entity}"')
def step_impl(context, entity_type: str, entity_name: str, target_entity: str):
    extras = {
        'favouriteAuthorId': getattr(context, target_entity)['id'],
    }
    _put_entity(context, entity_type, entity_name, extras)


@given('I put an example "related-book" entity called "{entity_name}" joining "{book1}" to "{book2}"')
def step_impl(context, entity_name: str, book1: str, book2: str):
    extras = {
        'book1Id': getattr(context, book1)['id'],
        'book2Id': getattr(context, book2)['id'],
    }
    _put_entity(context, 'related-book', entity_name, extras)


@given('I put an example "{entity_type}" entity called "{entity_name}"')
def step_impl(context, entity_type: str, entity_name: str):
    _put_entity(context, entity_type, entity_name, {})


def _put_entity(context, entity_type: str, entity_name: str, extras: Mapping[str, str]):
    entity = example_entity_generators[entity_type]()
    entity_id = entity['id']
    entity.update(extras)
    setattr(context, entity_name, entity)
    response = make_request(
        client=context.client, endpoint=f'{entity_type}/{entity_id}',
        method='put', data=entity,
    )
    assert_that(response.status_code, equal_to(201))


@when('I "{verb}" a "book_genre" join entity')
def step_impl(context, verb):
    book_uuid =  context.book_entity['id']
    genre_uuid = context.genre_entity['id']
    book_genre_entity = generate_example_book_genre(
        book_uuid=book_uuid, genre_uuid=genre_uuid,
    )
    context.book_genre_uuid = book_genre_uuid = book_genre_entity['id']
    if verb.lower() == 'put':
        response = make_request(client=context.client, endpoint=f'book-genre/{book_genre_uuid}',
                                method=verb, data=book_genre_entity)
    elif verb.lower() == 'post':
        response = make_request(client=context.client, endpoint=f'book-genre',
                                method=verb, data=book_genre_entity)
    assert_that(response.status_code, equal_to(201))


@when('I list "{entity_type}" filtered by "{parameters}"')
def step_impl(context, entity_type: str, parameters: str):
    context.response = make_request(
        client=context.client,
        endpoint=entity_type,
        method='get',
        parameters=parameters,
    )


@then('I have "{count}" results')
def step_impl(context, count: str):
    assert_that(len(context.response.json['data']), int(count))


@then('I can see that genre in the response from "{url}"')
def step_impl(context, url: str):
    url = url.replace('{id}', context.book_entity['id'])
    response = make_request(client=context.client, endpoint=url, method='get')
    assert_that(response.status_code, equal_to(200))
    data = json.loads(response.data)
    genre = data['genre']
    assert_that(genre['id'], equal_to(context.genre_entity['id']))


@step('I patch that "{entity_name}" entity with that "{entity_id}" id')
def step_impl(context, entity_name: str, entity_id: str):
    patch_id = getattr(context, f'{entity_id}_entity')['id']
    existing_entity_id = getattr(context, f'{entity_name}_entity')['id']
    data = {
        f"{entity_id}Id": patch_id,
    }
    response = make_request(client=context.client, endpoint=f'{entity_name}/{existing_entity_id}',
                            method='patch', data=data)
    assert_that(response.status_code, equal_to(200))


@step('I can see that book in the response from "{url}"')
def step_impl(context, url: str):
    url = url.replace('{id}', context.author_entity['id'])
    response = make_request(client=context.client, endpoint=url, method='get')
    assert_that(response.status_code, equal_to(200))
    data = response.json
    existing_book = getattr(context, 'book_entity')
    for book in data['books']:
        if existing_book['id'] == book['id']:
            return
    raise Exception(f'Book with id {existing_book["id"]} not found')


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
    context.book_entity = book = {
        **book,
        **{'authorId': context.author_entity['id']}
    }
    response = make_request(client=context.client, endpoint=f'book/{book["id"]}',
                            method='put', data=book)
    assert_that(response.status_code, equal_to(201))


@step("I also put a collaborator relationship to that author")
def step_impl(context):
    context.book_entity['collaboratorId'] = context.author_entity['id']
    book = context.book_entity
    response = make_request(client=context.client, endpoint=f'book/{book["id"]}',
                            method='put', data=book)
    assert_that(response.status_code, equal_to(201))


@step("I put an author called {author_name} with a relationship to that author on {relationship}")
def step_impl(context, author_name, relationship):
    related_author = generate_example_author()
    setattr(context, author_name, related_author)
    response = make_request(
        client=context.client, endpoint=f'author/{related_author["id"]}',
        method='put', data=related_author)
    assert_that(response.status_code, equal_to(201))

    context.author_entity[relationship] = related_author['id']
    author = context.author_entity
    response = make_request(
        client=context.client, endpoint=f'author/{author["id"]}',
        method='put', data=author)
    assert_that(response.status_code, equal_to(201))


@when("I get that book entity")
def step_impl(context):
    book = context.book_entity
    url = f'/book/{book["id"]}'
    response = make_request(client=context.client, endpoint=url, method='get')
    assert_that(response.status_code, equal_to(200))
    data = json.loads(response.data)
    context.retrieved_book = data


@step("I can see that author in the response")
def step_impl(context):
    author = context.retrieved_book['author']
    assert_that(author['id'], equal_to(context.author_entity['id']))


@when('I get that "{entity_type}" SQLAlchemy model')
def step_impl(context, entity_type: str):
    entity = context.author_entity if entity_type == 'author' else context.book_entity

    _get_sqlalchemy_model(context, entity_type, entity)


@when('I get the "{entity_type}" called "{entity_name}" SQLAlchemy model')
def step_impl(context, entity_type: str, entity_name: str):
    entity = getattr(context, entity_name)

    _get_sqlalchemy_model(context, entity_type, entity)


def _get_sqlalchemy_model(context, entity_type, entity):
    from bookshop import app
    context.app_context = app.app_context()
    context.app_context.push()
    if entity_type == 'author':
        model = Author
        filter_ = Author.author_id == entity['id']
    elif entity_type == 'book':
        model = Book
        filter_ = Book.book_id == entity['id']
    else:
        raise Exception('Only supports books and authors')

    setattr(
        context,
        f'sql_{entity_type}',
        getattr(model, 'query').filter(filter_).one()
    )


@then('"{target}" should have "{n}" items in it')
def step_impl(context, target: str, n: str):
    length = len(_extract_target(context, target))
    assert_that(length, equal_to(int(n)))
    context.app_context.pop()


@then('"{target}" should be that author')
def step_impl(context, target):
    author = Author.query.filter(Author.author_id == context.author_entity['id']).one()
    assert_that(_extract_target(context, target), equal_to(author))


@then('"{target}" should be "{context_name}"')
def step_impl(context, target, context_name):
    assert_that(
        _extract_target(context, target),
        getattr(context, context_name),
    )


@then('"{target}" should be None')
def step_impl(context, target):
    assert_that(_extract_target(context, target), none())


@then('"{target}" should be a recent timestamp')
def step_impl(context, target):
    expected = datetime.datetime.utcnow()
    delta = datetime.timedelta(seconds=2)
    found = _extract_target(context, target)

    assert_that(abs(found - expected).seconds, less_than(delta.seconds))


@when('I save the value of "{target}" as "{save_name}"')
def step_impl(context, target, save_name):
    found = _extract_target(context, target)
    context.saved_values = getattr(context, 'saved_values', {})
    context.saved_values[save_name] = found


@then('"{target}" should not equal saved value "{save_name}"')
def step_impl(context, target, save_name):
    assert_that(_extract_target(context, target), is_not(equal_to(context.saved_values[save_name])))


def _extract_target(context, target):
    if isinstance(target, str):
        target = target.split('.')
    if len(target) == 0:
        return context
    else:
        return _extract_target(getattr(context, target[0]), target[1:])


@when('I patch that "{entity_name}" entity to set "{prop}" to "{value}"')
def step_impl(context, entity_name, prop, value):
    existing_entity_id = getattr(context, f'{entity_name}_entity')['id']
    data = {
        prop: value
    }
    response = make_request(client=context.client, endpoint=f'{entity_name}/{existing_entity_id}',
                            method='patch', data=data)
    assert_that(response.status_code, equal_to(200))


@then('I can see that "{entity_name}" has "{prop}" set to "{value}"')
def step_impl(context, entity_name, prop, value):
    existing_entity = getattr(context, f'{entity_name}_entity')
    response = make_request(client=context.client, endpoint=f'{entity_name}/{existing_entity["id"]}',
                            method='get')
    assert_that(response.status_code, equal_to(200))
    data = response.json
    assert_that(data[prop], equal_to(value))
