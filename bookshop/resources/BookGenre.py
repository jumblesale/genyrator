import json
from typing import Optional

from flask import request, abort, url_for
from flask_restplus import Resource, fields, Namespace

from sqlalchemy.orm import noload

from bookshop.core.convert_dict import (
    python_dict_to_json_dict, json_dict_to_python_dict
)
from bookshop.sqlalchemy import db
from bookshop.sqlalchemy.model import BookGenre
from bookshop.sqlalchemy.convert_properties import (
    convert_properties_to_sqlalchemy_properties, convert_sqlalchemy_properties_to_dict_properties
)
from bookshop.sqlalchemy.join_entities import create_joined_entity_map
from bookshop.schema import BookGenreSchema
from bookshop.sqlalchemy.model_to_dict import model_to_dict
from bookshop.sqlalchemy.convert_dict_to_marshmallow_result import convert_dict_to_marshmallow_result
from bookshop.domain.BookGenre import book_genre as book_genre_domain_model

api = Namespace('book_genres',
                path='/',
                description='Bookgenre API', )

book_genre_model = api.model('BookGenre', {
    'id': fields.String(),
    'bookId': fields.String(),
    'genreId': fields.String(),
    'book': fields.Raw(),
    'genre': fields.Raw(),
})

book_genre_schema = BookGenreSchema()
book_genres_many_schema = BookGenreSchema(many=True)


@api.route('/book-genre/<bookGenreId>', endpoint='book_genre_by_id')  # noqa: E501
class BookGenreResource(Resource):  # type: ignore
    @api.doc(id='get-book_genre-by-id', responses={401: 'Unauthorised', 404: 'Not Found'})  # noqa: E501
    @api.marshal_with(book_genre_model)
    def get(self, bookGenreId):  # type: ignore
        result: Optional[BookGenre] = BookGenre.query.filter_by(book_genre_id=bookGenreId).first()  # noqa: E501
        if result is None:
            abort(404)
        response = python_dict_to_json_dict(model_to_dict(
            result,
        )), 200
        return response

    @api.doc(id='delete-book_genre-by-id', responses={401: 'Unauthorised', 404: 'Not Found'})
    def delete(self, bookGenreId):  # type: ignore
        result: Optional[BookGenre] = BookGenre.query.filter_by(book_genre_id=bookGenreId).delete()
        if result != 1:
            abort(404)
        db.session.commit()
        return '', 204

    @api.expect(book_genre_model, validate=False)
    @api.marshal_with(book_genre_model)
    def put(self, bookGenreId):  # type: ignore
        data = json.loads(request.data)
        if type(data) is not dict:
            return abort(400)

        if 'id' not in data:
            data['id'] = bookGenreId

        marshmallow_schema_or_errors = convert_dict_to_marshmallow_result(
            data=data,
            identifier=bookGenreId,
            identifier_column='book_genre_id',
            domain_model=book_genre_domain_model,
            sqlalchemy_model=BookGenre,
            schema=book_genre_schema,
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

    @api.expect(book_genre_model, validate=False)
    def patch(self, bookGenreId):  # type: ignore
        result: Optional[BookGenre] = BookGenre.query.filter_by(book_genre_id=bookGenreId)\
            .options(noload('*')).first()  # noqa: E501

        if result is None:
            abort(404)

        data = json.loads(request.data)

        if type(data) is not dict:
            return abort(400)

        marshmallow_schema_or_errors = convert_dict_to_marshmallow_result(
            data=json_dict_to_python_dict(model_to_dict(result)),
            identifier=bookGenreId,
            identifier_column='book_genre_id',
            domain_model=book_genre_domain_model,
            sqlalchemy_model=BookGenre,
            schema=book_genre_schema,
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
    

@api.route('/book-genres', endpoint='book_genres')  # noqa: E501
class ManyBookGenreResource(Resource):  # type: ignore
    def get(self):
        query = BookGenre.query
        param_book_genre_id = request.args.get('book_genre_id')
        if param_book_genre_id:
            query = query.filter_by(book_genre_id=param_book_genre_id)
        param_book_id = request.args.get('book_id')
        if param_book_id:
            query = query.filter_by(book_id=param_book_id)
        param_genre_id = request.args.get('genre_id')
        if param_genre_id:
            query = query.filter_by(genre_id=param_genre_id)
        result = query.all()
        urls = [
            url_for(
                'book_genre_by_id',
                bookGenreId=x.book_genre_id
            )
            for x in result
        ]
        return {"links": urls}

    def post(self):  # type: ignore
        ...
