import json
from typing import Optional

from flask import request, abort, url_for
from flask_restplus import Resource, fields, Namespace


from bookshop.core.convert_dict import (
    python_dict_to_json_dict, json_dict_to_python_dict
)
from bookshop.sqlalchemy import db
from bookshop.sqlalchemy.model import Genre
from bookshop.sqlalchemy.convert_properties import (
    convert_properties_to_sqlalchemy_properties, convert_sqlalchemy_properties_to_dict_properties
)
from bookshop.sqlalchemy.join_entities import create_joined_entity_map
from bookshop.schema import GenreSchema
from bookshop.sqlalchemy.model_to_dict import model_to_dict
from bookshop.sqlalchemy.convert_dict_to_marshmallow_result import convert_dict_to_marshmallow_result
from bookshop.domain.Genre import genre as genre_domain_model

api = Namespace('genres',
                path='/',
                description='Genre API', )

genre_model = api.model('Genre', {
    'id': fields.String(attribute='genreId'),
    'title': fields.String(),
})

genre_schema = GenreSchema()
genres_many_schema = GenreSchema(many=True)


@api.route('/genre/<genreId>', endpoint='genre_by_id')  # noqa: E501
class GenreResource(Resource):  # type: ignore
    @api.doc(id='get-genre-by-id', responses={401: 'Unauthorised', 404: 'Not Found'})  # noqa: E501
    def get(self, genreId):  # type: ignore
        result: Optional[Genre] = Genre.query.filter_by(genre_id=genreId).first()  # noqa: E501
        if result is None:
            abort(404)
        response = model_to_dict(
            result,
        ), 200
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

        return model_to_dict(
            marshmallow_schema_or_errors.data,
        ), 201

    @api.expect(genre_model, validate=False)
    def patch(self, genreId):  # type: ignore
        result: Optional[Genre] = Genre.query.filter_by(genre_id=genreId).first()  # noqa: E501

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

        return model_to_dict(
            marshmallow_schema_or_errors.data,
        ), 200
    

@api.route('/genres', endpoint='genres')  # noqa: E501
class ManyGenreResource(Resource):  # type: ignore
    def get(self):
        result = Genre.query.all()
        urls = [
            url_for(
                'genre_by_id',
                genreId=x.genre_id
            )
            for x in result
        ]
        return {"links": urls}

    def post(self):  # type: ignore
        ...
