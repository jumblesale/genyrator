import json
from typing import Optional

from flask import request, abort, url_for
from flask_restplus import Resource, fields, Namespace
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import noload

from bookshop.core.convert_dict import (
    python_dict_to_json_dict, json_dict_to_python_dict
)
from bookshop.sqlalchemy import db
from bookshop.sqlalchemy.model import Author
from bookshop.sqlalchemy.convert_properties import (
    convert_properties_to_sqlalchemy_properties, convert_sqlalchemy_properties_to_dict_properties
)
from bookshop.schema import AuthorSchema
from bookshop.sqlalchemy.model_to_dict import model_to_dict
from bookshop.sqlalchemy.convert_dict_to_marshmallow_result import convert_dict_to_marshmallow_result
from bookshop.domain.Author import author as author_domain_model

api = Namespace('authors',
                path='/',
                description='Author API', )

author_model = api.model('Author', {
    'id': fields.String(),
    'name': fields.String(),
    'favouriteAuthorId': fields.String(),
    'hatedAuthorId': fields.String(),
    'books': fields.Raw(),
    'favouriteBook': fields.Raw(),
    'collaborations': fields.Raw(),
})

author_schema = AuthorSchema()
authors_many_schema = AuthorSchema(many=True)


@api.route('/author/<authorId>', endpoint='author_by_id')  # noqa: E501
class AuthorResource(Resource):  # type: ignore
    @api.doc(id='get-author-by-id', responses={401: 'Unauthorised', 404: 'Not Found'})  # noqa: E501
    @api.marshal_with(author_model)
    def get(self, authorId):  # type: ignore
        result: Optional[Author] = Author.query.filter_by(author_id=authorId).first()  # noqa: E501
        if result is None:
            abort(404)
        response = python_dict_to_json_dict(model_to_dict(
            result,
        )), 200
        return response

    @api.doc(id='delete-author-by-id', responses={401: 'Unauthorised', 404: 'Not Found'})
    def delete(self, authorId):  # type: ignore
        result: Optional[Author] = Author.query.filter_by(author_id=authorId).delete()
        if result != 1:
            abort(404)
        db.session.commit()
        return '', 204

    @api.expect(author_model, validate=False)
    @api.marshal_with(author_model)
    def put(self, authorId):  # type: ignore
        data = json.loads(request.data)
        if type(data) is not dict:
            return abort(400)

        if 'id' not in data:
            data['id'] = authorId

        marshmallow_schema_or_errors = convert_dict_to_marshmallow_result(
            data=data,
            identifier=authorId,
            identifier_column='author_id',
            domain_model=author_domain_model,
            sqlalchemy_model=Author,
            schema=author_schema,
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

    @api.expect(author_model, validate=False)
    def patch(self, authorId):  # type: ignore
        result: Optional[Author] = Author.query.filter_by(author_id=authorId)\
            .options(noload('*')).first()  # noqa: E501

        if result is None:
            abort(404)

        data = json.loads(request.data)

        if type(data) is not dict:
            return abort(400)

        marshmallow_schema_or_errors = convert_dict_to_marshmallow_result(
            data=json_dict_to_python_dict(model_to_dict(result)),
            identifier=authorId,
            identifier_column='author_id',
            domain_model=author_domain_model,
            sqlalchemy_model=Author,
            schema=author_schema,
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
    

@api.route('/author', endpoint='authors')  # noqa: E501
class ManyAuthorResource(Resource):  # type: ignore
    def get(self):
        query = Author.query
        param_author_id = request.args.get('author_id')
        if param_author_id:
            query = query.filter_by(author_id=param_author_id)
        param_name = request.args.get('name')
        if param_name:
            query = query.filter_by(name=param_name)
        param_favourite_author_id = request.args.get('favourite_author_id')
        if param_favourite_author_id:
            query = query.filter_by(favourite_author_id=param_favourite_author_id)
        param_hated_author_id = request.args.get('hated_author_id')
        if param_hated_author_id:
            query = query.filter_by(hated_author_id=param_hated_author_id)
        result = query.all()
        return python_dict_to_json_dict({"data": [model_to_dict(r) for r in result]})

    def post(self):  # type: ignore
        ...


@api.route('/author/<authorId>/books/reviews', endpoint='books-review')  # noqa: E501
class Review(Resource):  # type: ignore
    @api.doc(id='books-review', responses={401: 'Unauthorised', 404: 'Not Found'})  # noqa: E501
    def get(self, authorId):  # type: ignore
        result: Optional[Author] = Author \
            .query \
            .options(
                joinedload('books')
                .joinedload('review')
            ) \
            .filter_by(
                author_id=authorId) \
            .first()  # noqa: E501
        if result is None:
            abort(404)
        result_dict = python_dict_to_json_dict(model_to_dict(
            sqlalchemy_model=result,
            paths=[
                'books',
                'review',
            ],
        ))

        return result_dict


@api.route('/author/<authorId>/books', endpoint='author-books')  # noqa: E501
class Books(Resource):  # type: ignore
    @api.doc(id='author-books', responses={401: 'Unauthorised', 404: 'Not Found'})  # noqa: E501
    def get(self, authorId):  # type: ignore
        result: Optional[Author] = Author \
            .query \
            .options(
                joinedload('books')
            ) \
            .filter_by(
                author_id=authorId) \
            .first()  # noqa: E501
        if result is None:
            abort(404)
        result_dict = python_dict_to_json_dict(model_to_dict(
            sqlalchemy_model=result,
            paths=[
                'books',
            ],
        ))

        return result_dict
