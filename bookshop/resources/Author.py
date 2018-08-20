import json
from flask import request, abort, url_for
from flask_restplus import Resource, fields, Namespace

from sqlalchemy.orm import joinedload

from typing import Optional
from bookshop.core.convert_dict import (
    python_dict_to_json_dict, json_dict_to_python_dict
)
from bookshop.sqlalchemy import db
from bookshop.sqlalchemy.model import Author
from bookshop.schema import AuthorSchema
from bookshop.sqlalchemy.model_to_dict import model_to_dict

api = Namespace('authors',
                path='/',
                description='Author API', )

author_model = api.model('Author', {
    'authorId': fields.String(),
    'name': fields.String(),
    'review': fields.Url('Author-Book-Review'),  # noqa: E501
})

author_schema = AuthorSchema()
authors_many_schema = AuthorSchema(many=True)


@api.route('/author/<authorId>', endpoint='author_by_id')  # noqa: E501
class AuthorResource(Resource):  # type: ignore

    @api.marshal_with(author_model)
    @api.doc(id='get-author-by-id', responses={401: 'Unauthorised', 404: 'Not Found'})  # noqa: E501
    def get(self, authorId):  # type: ignore
        result: Optional[Author] = Author.query.filter_by(author_id=authorId).first()  # noqa: E501
        if result is None:
            abort(404)
        return python_dict_to_json_dict(model_to_dict(result))

    @api.doc(id='delete-author-by-id', responses={401: 'Unauthorised', 404: 'Not Found'})
    def delete(self, authorId):  # type: ignore
        result: Optional[Author] = Author.query.filter_by(author_id=authorId).delete()
        if result != 1:
            abort(404)
        db.session.commit()
        return '', 204

    @api.expect(author_model, validate=False)
    def put(self, authorId):  # type: ignore
        data = json.loads(request.data)
        if type(data) is not dict:
            return abort(400)

        result: Optional[Author] = Author.query.filter_by(author_id=authorId).first()  # noqa: E501

        if 'authorId' not in data:
            data['authorId'] = uuid4(authorId)

        marshmallow_result = author_schema.load(
            json_dict_to_python_dict(data),
            session=db.session,
            instance=result,
        )
        if marshmallow_result.errors:
            abort(400, python_dict_to_json_dict(marshmallow_result.errors))

        db.session.add(marshmallow_result.data)
        db.session.commit()
        return '', 201

    @api.expect(author_model, validate=False)
    def patch(self, authorId):  # type: ignore
        data = json.loads(request.data)
        if type(data) is not dict:
            return abort(400)

        result: Optional[Author] = Author.query.filter_by(author_id=authorId).first()

        if result is None:
            abort(404)

        if 'authorId' not in data:
            data['authorId'] = uuid4(authorId)

        python_dict = json_dict_to_python_dict(data)
        [setattr(result, k, v) for k, v in python_dict.items()]

        db.session.add(result)
        db.session.commit()


@api.route('/authors', endpoint='authors')  # noqa: E501
class ManyAuthorResource(Resource):  # type: ignore

    def get(self):
        result = Author.query.all()
        urls = [
            url_for(
                'author_by_id',
                authorId=x.author_id
            )
            for x in result
        ]
        return {"links": urls}

    def post(self):  # type: ignore
        ...


@api.route('/author/<authorId>/books/reviews', endpoint='Author-Book-Review')  # noqa: E501
class Review(Resource):  # type: ignore
    @api.doc(id='Author-Book-Review', responses={401: 'Unauthorised', 404: 'Not Found'})  # noqa: E501
    def get(self, authorId):  # type: ignore
        result: Optional[Author] = Author \
            .query \
            .options(
                joinedload('Author')
                .joinedload('Book')
                .joinedload('Review')
            ) \
            .filter_by(author_id=authorId) \
            .first()  # noqa: E501
        if result is None:
            abort(404)
        return python_dict_to_json_dict(model_to_dict(result, ['Author', 'Book', 'Review']))  # noqa: E501
