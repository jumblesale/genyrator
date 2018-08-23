import json
from flask import request, abort, url_for
from flask_restplus import Resource, fields, Namespace

from typing import Optional
from uuid import UUID

from bookshop.core.convert_dict import (
    python_dict_to_json_dict, json_dict_to_python_dict
)
from bookshop.sqlalchemy import db
from bookshop.sqlalchemy.model import BookGenre
from bookshop.schema import BookGenreSchema
from bookshop.sqlalchemy.model_to_dict import model_to_dict

api = Namespace('book_genres',
                path='/',
                description='Bookgenre API', )

book_genre_model = api.model('BookGenre', {
    'bookGenreId': fields.String(),
    'bookId': fields.String(),
    'genreId': fields.String(),
})

book_genre_schema = BookGenreSchema()
book_genres_many_schema = BookGenreSchema(many=True)


@api.route('/book-genre/<bookGenreId>', endpoint='book_genre_by_id')  # noqa: E501
class BookGenreResource(Resource):  # type: ignore

    @api.marshal_with(book_genre_model)
    @api.doc(id='get-book_genre-by-id', responses={401: 'Unauthorised', 404: 'Not Found'})  # noqa: E501
    def get(self, bookGenreId):  # type: ignore
        result: Optional[BookGenre] = BookGenre.query.filter_by(book_genre_id=bookGenreId).first()  # noqa: E501
        if result is None:
            abort(404)
        return python_dict_to_json_dict(model_to_dict(result))

    @api.doc(id='delete-book_genre-by-id', responses={401: 'Unauthorised', 404: 'Not Found'})
    def delete(self, bookGenreId):  # type: ignore
        result: Optional[BookGenre] = BookGenre.query.filter_by(book_genre_id=bookGenreId).delete()
        if result != 1:
            abort(404)
        db.session.commit()
        return '', 204

    @api.expect(book_genre_model, validate=False)
    def put(self, bookGenreId):  # type: ignore
        data = json.loads(request.data)
        if type(data) is not dict:
            return abort(400)

        result: Optional[BookGenre] = BookGenre.query.filter_by(book_genre_id=bookGenreId).first()  # noqa: E501

        if 'bookGenreId' not in data:
            data['bookGenreId'] = UUID(bookGenreId)

        marshmallow_result = book_genre_schema.load(
            json_dict_to_python_dict(data),
            session=db.session,
            instance=result,
        )
        if marshmallow_result.errors:
            abort(400, python_dict_to_json_dict(marshmallow_result.errors))

        db.session.add(marshmallow_result.data)
        db.session.commit()
        return '', 201

    @api.expect(book_genre_model, validate=False)
    def patch(self, bookGenreId):  # type: ignore
        data = json.loads(request.data)
        if type(data) is not dict:
            return abort(400)

        result: Optional[BookGenre] = BookGenre.query.filter_by(book_genre_id=bookGenreId).first()

        if result is None:
            abort(404)

        if 'bookGenreId' not in data:
            data['bookGenreId'] = UUID(bookGenreId)

        python_dict = json_dict_to_python_dict(data)
        [setattr(result, k, v) for k, v in python_dict.items()]

        db.session.add(result)
        db.session.commit()


@api.route('/book-genres', endpoint='book_genres')  # noqa: E501
class ManyBookGenreResource(Resource):  # type: ignore

    def get(self):
        result = BookGenre.query.all()
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
