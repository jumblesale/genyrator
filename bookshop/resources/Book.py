import json
from typing import Optional
from uuid import UUID

from flask import request, abort, url_for
from flask_restplus import Resource, fields, Namespace

from sqlalchemy.orm import joinedload


from bookshop.core.convert_dict import (
    python_dict_to_json_dict, json_dict_to_python_dict
)
from bookshop.sqlalchemy import db
from bookshop.sqlalchemy.model import Book
from bookshop.sqlalchemy.convert_properties import convert_properties_to_sqlalchemy_properties
from bookshop.sqlalchemy.join_entities import create_joined_entity_map
from bookshop.schema import BookSchema
from bookshop.sqlalchemy.model_to_dict import model_to_dict
from bookshop.domain.Book import book as book_domain_model

api = Namespace('books',
                path='/',
                description='Book API', )

book_model = api.model('Book', {
    'bookId': fields.String(),
    'name': fields.String(),
    'rating': fields.Integer(),
    'authorId': fields.String(),
    'genre': fields.Url('genre'),  # noqa: E501
})

book_schema = BookSchema()
books_many_schema = BookSchema(many=True)


@api.route('/book/<bookId>', endpoint='book_by_id')  # noqa: E501
class BookResource(Resource):  # type: ignore

    @api.marshal_with(book_model)
    @api.doc(id='get-book-by-id', responses={401: 'Unauthorised', 404: 'Not Found'})  # noqa: E501
    def get(self, bookId):  # type: ignore
        result: Optional[Book] = Book.query.filter_by(book_id=bookId).first()  # noqa: E501
        if result is None:
            abort(404)
        return python_dict_to_json_dict(model_to_dict(result))

    @api.doc(id='delete-book-by-id', responses={401: 'Unauthorised', 404: 'Not Found'})
    def delete(self, bookId):  # type: ignore
        result: Optional[Book] = Book.query.filter_by(book_id=bookId).delete()
        if result != 1:
            abort(404)
        db.session.commit()
        return '', 204

    @api.expect(book_model, validate=False)
    def put(self, bookId):  # type: ignore
        data = json.loads(request.data)
        if type(data) is not dict:
            return abort(400)

        result: Optional[Book] = Book.query.filter_by(book_id=bookId).first()  # noqa: E501

        joined_entities = create_joined_entity_map(
            book_domain_model,
            data,
        )

        data = convert_properties_to_sqlalchemy_properties(
            book_domain_model,
            joined_entities,
            json_dict_to_python_dict(data),
        )

        marshmallow_result = book_schema.load(
            json_dict_to_python_dict(data),
            session=db.session,
            instance=result,
        )
        if marshmallow_result.errors:
            abort(400, python_dict_to_json_dict(marshmallow_result.errors))

        db.session.add(marshmallow_result.data)
        db.session.commit()
        return '', 201

    @api.expect(book_model, validate=False)
    def patch(self, bookId):  # type: ignore
        data = json.loads(request.data)
        if type(data) is not dict:
            return abort(400)

        result: Optional[Book] = Book.query.filter_by(book_id=bookId).first()

        if result is None:
            abort(404)

        python_dict = json_dict_to_python_dict(data)
        [setattr(result, k, v) for k, v in python_dict.items()]

        db.session.add(result)
        db.session.commit()


@api.route('/books', endpoint='books')  # noqa: E501
class ManyBookResource(Resource):  # type: ignore

    def get(self):
        result = Book.query.all()
        urls = [
            url_for(
                'book_by_id',
                bookId=x.book_id
            )
            for x in result
        ]
        return {"links": urls}

    def post(self):  # type: ignore
        ...


@api.route('/book/<bookId>/genres', endpoint='genre')  # noqa: E501
class Genre(Resource):  # type: ignore
    @api.doc(id='genre', responses={401: 'Unauthorised', 404: 'Not Found'})  # noqa: E501
    def get(self, bookId):  # type: ignore
        result: Optional[Book] = Book \
            .query \
            .options(
                joinedload('genre')
            ) \
            .filter_by(book_id=bookId) \
            .first()  # noqa: E501
        if result is None:
            abort(404)
        return model_to_dict(result, ['genre'])  # noqa: E501
