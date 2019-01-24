import json
import uuid
from typing import Optional

from flask import request, abort, url_for
from flask_restplus import Resource, fields, Namespace

from sqlalchemy.orm import noload

from bookshop.core.convert_dict import (
    python_dict_to_json_dict, json_dict_to_python_dict
)
from bookshop.sqlalchemy import db
from bookshop.sqlalchemy.model import Genre
from bookshop.sqlalchemy.convert_properties import (
    convert_properties_to_sqlalchemy_properties, convert_sqlalchemy_properties_to_dict_properties
)
from bookshop.schema import GenreSchema
from bookshop.sqlalchemy.model_to_dict import model_to_dict
from bookshop.sqlalchemy.convert_dict_to_marshmallow_result import convert_dict_to_marshmallow_result
from bookshop.domain.Genre import genre as genre_domain_model

api = Namespace('genres',
                path='/',
                description='Genre API', )

genre_model = api.model('Genre', {
    'id': fields.String(),
    'title': fields.String(),
    'book': fields.Raw(),
})

genre_schema = GenreSchema()
genres_many_schema = GenreSchema(many=True)


@api.route('/genre/<genreId>', endpoint='genre_by_id')  # noqa: E501
class GenreResource(Resource):  # type: ignore
    @api.doc(id='get-genre-by-id', responses={401: 'Unauthorised', 404: 'Not Found'})  # noqa: E501
    @api.marshal_with(genre_model)
    def get(self, genreId):  # type: ignore
        result: Optional[Genre] = Genre.query.filter_by(genre_id=genreId).first()  # noqa: E501
        if result is None:
            abort(404)
        response = python_dict_to_json_dict(model_to_dict(
            result,
        )), 200
        return response

    @api.doc(id='delete-genre-by-id', responses={401: 'Unauthorised', 404: 'Not Found'})
    def delete(self, genreId):  # type: ignore
        result: Optional[Genre] = Genre.query.filter_by(genre_id=genreId).delete()
        if result != 1:
            abort(404)
        db.session.commit()
        return '', 204

    @api.expect(genre_model, validate=False)
    @api.marshal_with(genre_model)
    def put(self, genreId):  # type: ignore
        data = json.loads(request.data)
        if type(data) is not dict:
            return abort(400)

        if 'id' not in data:
            data['id'] = genreId

        marshmallow_schema_or_errors = convert_dict_to_marshmallow_result(
            data=data,
            identifier=genreId,
            identifier_column='genre_id',
            domain_model=genre_domain_model,
            sqlalchemy_model=Genre,
            schema=genre_schema,
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

    @api.expect(genre_model, validate=False)
    def patch(self, genreId):  # type: ignore
        result: Optional[Genre] = Genre.query.filter_by(genre_id=genreId)\
            .options(noload('*')).first()  # noqa: E501

        if result is None:
            abort(404)

        data = json.loads(request.data)

        if type(data) is not dict:
            return abort(400)

        marshmallow_schema_or_errors = convert_dict_to_marshmallow_result(
            data=json_dict_to_python_dict(model_to_dict(result)),
            identifier=genreId,
            identifier_column='genre_id',
            domain_model=genre_domain_model,
            sqlalchemy_model=Genre,
            schema=genre_schema,
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
    

@api.route('/genre', endpoint='genres')  # noqa: E501
class ManyGenreResource(Resource):  # type: ignore
    def get(self):
        query = Genre.query
        param_genre_id = request.args.get('genre_id')
        if param_genre_id:
            query = query.filter_by(genre_id=param_genre_id)
        param_title = request.args.get('title')
        if param_title:
            query = query.filter_by(title=param_title)
        result = query.all()
        return python_dict_to_json_dict({"data": [model_to_dict(r) for r in result]})

    def post(self):  # type: ignore
        data = request.get_json(force=True)
        if not isinstance(data, dict):
            return abort(400)

        data['genreId'] = uuid.uuid4()

        marshmallow_result = genre_schema.load(json_dict_to_python_dict(data), session=db.session)
        if marshmallow_result.errors:
            abort(400, marshmallow_result.errors)

        db.session.add(marshmallow_result.data)
        db.session.commit()

        return python_dict_to_json_dict(model_to_dict(
            marshmallow_result.data,
        )), 201
