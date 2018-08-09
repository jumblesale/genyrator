import json
from flask import request, abort, json as flask_json, url_for
from flask_restplus import Resource, fields, Namespace
from sqlalchemy.orm import joinedload
from typing import Optional
from bookshop.core.convert_dict import python_dict_to_json_dict, json_dict_to_python_dict
from bookshop.sqlalchemy import db
from bookshop.sqlalchemy.model import Book
from bookshop.schema import *
from bookshop.sqlalchemy.model_to_dict import model_to_dict

api = Namespace('books',
                path='/',
                description='Book API', )

book_model = api.model('Book', {
    'bookId': fields.String(),
    'name': fields.String(),
    'rating': fields.Integer(),
})

book_schema = BookSchema()
books_many_schema = BookSchema(many=True)


@api.route('/book/<bookId>', endpoint='book_by_id')
class BookResource(Resource):  # type: ignore
    @api.marshal_with(book_model)
    @api.doc(id='get-book-by-id', responses={401: 'Unauthorised', 404: 'Not Found'})
    def get(self, bookId):  # type: ignore
        result: Optional[Book] = Book.query.filter_by(book_id=bookId).first()
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

        result: Optional[Book] = Book.query.filter_by(book_id=bookId).first()

        if 'bookId' not in data:
            data['bookId'] = str(bookId)

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

        if 'bookId' not in data:
            data['bookId'] = str(bookId)

        python_dict = json_dict_to_python_dict(data)
        [setattr(result, k, v) for k, v in python_dict.items()]

        db.session.add(result)
        db.session.commit()


@api.route('/books', endpoint='books')
class ManyBookResource(Resource):  # type: ignore
    def get(self):
        result = Book.query.all()
        urls = [url_for('book_by_id', bookId=x.book_id) for x in result]
        return {"links": urls}

    
    
    def post(self):  # type: ignore
        ...
