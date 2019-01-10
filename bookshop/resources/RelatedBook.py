import json
from typing import Optional

from flask import request, abort, url_for
from flask_restplus import Resource, fields, Namespace

from sqlalchemy.orm import noload

from bookshop.core.convert_dict import (
    python_dict_to_json_dict, json_dict_to_python_dict
)
from bookshop.sqlalchemy import db
from bookshop.sqlalchemy.model import RelatedBook
from bookshop.sqlalchemy.convert_properties import (
    convert_properties_to_sqlalchemy_properties, convert_sqlalchemy_properties_to_dict_properties
)
from bookshop.sqlalchemy.join_entities import create_joined_entity_map
from bookshop.schema import RelatedBookSchema
from bookshop.sqlalchemy.model_to_dict import model_to_dict
from bookshop.sqlalchemy.convert_dict_to_marshmallow_result import convert_dict_to_marshmallow_result
from bookshop.domain.RelatedBook import related_book as related_book_domain_model

api = Namespace('related_books',
                path='/',
                description='Relatedbook API', )

related_book_model = api.model('RelatedBook', {
    'id': fields.String(),
    'book1Id': fields.String(),
    'book2Id': fields.String(),
    'book1': fields.Raw(),
    'book2': fields.Raw(),
})

related_book_schema = RelatedBookSchema()
related_books_many_schema = RelatedBookSchema(many=True)


@api.route('/related-book/<relatedBookUuid>', endpoint='related_book_by_id')  # noqa: E501
class RelatedBookResource(Resource):  # type: ignore
    @api.doc(id='get-related_book-by-id', responses={401: 'Unauthorised', 404: 'Not Found'})  # noqa: E501
    @api.marshal_with(related_book_model)
    def get(self, relatedBookUuid):  # type: ignore
        result: Optional[RelatedBook] = RelatedBook.query.filter_by(related_book_uuid=relatedBookUuid).first()  # noqa: E501
        if result is None:
            abort(404)
        response = python_dict_to_json_dict(model_to_dict(
            result,
        )), 200
        return response

    @api.doc(id='delete-related_book-by-id', responses={401: 'Unauthorised', 404: 'Not Found'})
    def delete(self, relatedBookUuid):  # type: ignore
        result: Optional[RelatedBook] = RelatedBook.query.filter_by(related_book_uuid=relatedBookUuid).delete()
        if result != 1:
            abort(404)
        db.session.commit()
        return '', 204

    @api.expect(related_book_model, validate=False)
    @api.marshal_with(related_book_model)
    def put(self, relatedBookUuid):  # type: ignore
        data = json.loads(request.data)
        if type(data) is not dict:
            return abort(400)

        if 'id' not in data:
            data['id'] = relatedBookUuid

        marshmallow_schema_or_errors = convert_dict_to_marshmallow_result(
            data=data,
            identifier=relatedBookUuid,
            identifier_column='related_book_uuid',
            domain_model=related_book_domain_model,
            sqlalchemy_model=RelatedBook,
            schema=related_book_schema,
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

    @api.expect(related_book_model, validate=False)
    def patch(self, relatedBookUuid):  # type: ignore
        result: Optional[RelatedBook] = RelatedBook.query.filter_by(related_book_uuid=relatedBookUuid)\
            .options(noload('*')).first()  # noqa: E501

        if result is None:
            abort(404)

        data = json.loads(request.data)

        if type(data) is not dict:
            return abort(400)

        marshmallow_schema_or_errors = convert_dict_to_marshmallow_result(
            data=json_dict_to_python_dict(model_to_dict(result)),
            identifier=relatedBookUuid,
            identifier_column='related_book_uuid',
            domain_model=related_book_domain_model,
            sqlalchemy_model=RelatedBook,
            schema=related_book_schema,
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
    

@api.route('/related-book', endpoint='related_books')  # noqa: E501
class ManyRelatedBookResource(Resource):  # type: ignore
    def get(self):
        query = RelatedBook.query
        param_related_book_uuid = request.args.get('related_book_uuid')
        if param_related_book_uuid:
            query = query.filter_by(related_book_uuid=param_related_book_uuid)
        param_book1_id = request.args.get('book1_id')
        if param_book1_id:
            query = query.filter_by(book1_id=param_book1_id)
        param_book2_id = request.args.get('book2_id')
        if param_book2_id:
            query = query.filter_by(book2_id=param_book2_id)
        result = query.all()
        return python_dict_to_json_dict({"data": [model_to_dict(r) for r in result]})

    def post(self):  # type: ignore
        ...
