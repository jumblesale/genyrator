import uuid
from typing import Optional

from flask import request, abort, url_for
from flask_restplus import Resource, fields, Namespace
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import noload

from bookshop.core.convert_dict import (
    python_dict_to_json_dict, json_dict_to_python_dict
)
from bookshop.sqlalchemy import db
from bookshop.sqlalchemy.model import Book
from bookshop.sqlalchemy.convert_properties import (
    convert_properties_to_sqlalchemy_properties, convert_sqlalchemy_properties_to_dict_properties
)
from bookshop.schema import BookSchema
from bookshop.sqlalchemy.model_to_dict import model_to_dict
from bookshop.sqlalchemy.convert_dict_to_marshmallow_result import convert_dict_to_marshmallow_result
from bookshop.domain.Book import book as book_domain_model

api = Namespace('books',
                path='/',
                description='Book API', )

book_model = api.model('Book', {
    'id': fields.String(),
    'name': fields.String(),
    'rating': fields.Float(),
    'authorId': fields.String(),
    'collaboratorId': fields.String(),
    'published': fields.Date(),
    'created': fields.DateTime(),
    'updated': fields.DateTime(),
    'author': fields.Raw(),
    'collaborator': fields.Raw(),
    'genre': fields.Raw(),
})

book_schema = BookSchema()
books_many_schema = BookSchema(many=True)


@api.route('/book/<bookId>', endpoint='book_by_id')  # noqa: E501
class BookResource(Resource):  # type: ignore
    @api.doc(id='get-book-by-id', responses={401: 'Unauthorised', 404: 'Not Found'})  # noqa: E501
    @api.marshal_with(book_model)
    def get(self, bookId):  # type: ignore
        result: Optional[Book] = Book.query.filter_by(book_id=bookId).first()  # noqa: E501
        if result is None:
            abort(404)
        response = python_dict_to_json_dict(model_to_dict(
            result,
        )), 200
        return response

    @api.doc(id='delete-book-by-id', responses={401: 'Unauthorised', 404: 'Not Found'})
    def delete(self, bookId):  # type: ignore
        result: Optional[Book] = Book.query.filter_by(book_id=bookId).delete()
        if result != 1:
            abort(404)
        db.session.commit()
        return '', 204

    @api.expect(book_model, validate=False)
    @api.marshal_with(book_model)
    def put(self, bookId):  # type: ignore
        data = request.get_json(force=True)
        if not isinstance(data, dict):
            abort(400)

        if 'id' not in data:
            data['id'] = bookId

        marshmallow_schema_or_errors = convert_dict_to_marshmallow_result(
            data=data,
            identifier=bookId,
            identifier_column='book_id',
            domain_model=book_domain_model,
            sqlalchemy_model=Book,
            schema=book_schema,
        )

        if isinstance(marshmallow_schema_or_errors, list):
            abort(400, marshmallow_schema_or_errors)
        if marshmallow_schema_or_errors.errors:
            abort(400, python_dict_to_json_dict(marshmallow_schema_or_errors.errors))

        db.session.add(marshmallow_schema_or_errors.data)
        db.session.commit()

        return python_dict_to_json_dict(model_to_dict(
            marshmallow_schema_or_errors.data,
        )), 201

    @api.expect(book_model, validate=False)
    def patch(self, bookId):  # type: ignore
        result: Optional[Book] = Book.query.filter_by(book_id=bookId)\
            .options(noload('*')).first()  # noqa: E501

        if result is None:
            abort(404)

        data = request.get_json(force=True)
        if not isinstance(data, dict):
            abort(400)

        marshmallow_schema_or_errors = convert_dict_to_marshmallow_result(
            data=json_dict_to_python_dict(model_to_dict(result)),
            identifier=bookId,
            identifier_column='book_id',
            domain_model=book_domain_model,
            sqlalchemy_model=Book,
            schema=book_schema,
            patch_data=data,
        )

        if isinstance(marshmallow_schema_or_errors, list):
            abort(400, marshmallow_schema_or_errors)
        if marshmallow_schema_or_errors.errors:
            abort(400, python_dict_to_json_dict(marshmallow_schema_or_errors.errors))

        db.session.add(marshmallow_schema_or_errors.data)
        db.session.commit()

        return python_dict_to_json_dict(model_to_dict(
            marshmallow_schema_or_errors.data,
        )), 200
    

@api.route('/book', endpoint='books')  # noqa: E501
class ManyBookResource(Resource):  # type: ignore
    def get(self):
        query = Book.query
        param_book_id = request.args.get('book_id')
        if param_book_id:
            query = query.filter_by(book_id=param_book_id)
        param_name = request.args.get('name')
        if param_name:
            query = query.filter_by(name=param_name)
        param_rating = request.args.get('rating')
        if param_rating:
            query = query.filter_by(rating=param_rating)
        param_author_id = request.args.get('author_id')
        if param_author_id:
            query = query.filter_by(author_id=param_author_id)
        param_collaborator_id = request.args.get('collaborator_id')
        if param_collaborator_id:
            query = query.filter_by(collaborator_id=param_collaborator_id)
        param_published = request.args.get('published')
        if param_published:
            query = query.filter_by(published=param_published)
        param_created = request.args.get('created')
        if param_created:
            query = query.filter_by(created=param_created)
        param_updated = request.args.get('updated')
        if param_updated:
            query = query.filter_by(updated=param_updated)
        result = query.all()
        return python_dict_to_json_dict({"data": [model_to_dict(r) for r in result]})

    def post(self):  # type: ignore
        data = request.get_json(force=True)
        if not isinstance(data, dict):
            return abort(400)

        data['bookId'] = uuid.uuid4()

        marshmallow_schema_or_errors = convert_dict_to_marshmallow_result(
            data=data,
            identifier=data['bookId'],
            identifier_column='book_id',
            domain_model=book_domain_model,
            sqlalchemy_model=Book,
            schema=book_schema,
        )

        if isinstance(marshmallow_schema_or_errors, list):
            abort(400, marshmallow_schema_or_errors)
        if marshmallow_schema_or_errors.errors:
            abort(400, marshmallow_schema_or_errors)

        db.session.add(marshmallow_schema_or_errors.data)
        db.session.commit()

        return python_dict_to_json_dict(model_to_dict(
            marshmallow_schema_or_errors.data,
        )), 201


@api.route('/book/<bookId>/genres', endpoint='genre')  # noqa: E501
class Genre(Resource):  # type: ignore
    @api.doc(id='genre', responses={401: 'Unauthorised', 404: 'Not Found'})  # noqa: E501
    def get(self, bookId):  # type: ignore
        result: Optional[Book] = Book \
            .query \
            .options(
                joinedload('genre')
            ) \
            .filter_by(
                book_id=bookId) \
            .first()  # noqa: E501
        if result is None:
            abort(404)
        result_dict = python_dict_to_json_dict(model_to_dict(
            sqlalchemy_model=result,
            paths=[
                'genre',
            ],
        ))

        return result_dict
