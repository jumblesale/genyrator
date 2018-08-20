import json
from flask import request, abort, url_for
from flask_restplus import Resource, fields, Namespace

from typing import Optional
from bookshop.core.convert_dict import (
    python_dict_to_json_dict, json_dict_to_python_dict
)
from bookshop.sqlalchemy import db
from bookshop.sqlalchemy.model import Genre
from bookshop.schema import GenreSchema
from bookshop.sqlalchemy.model_to_dict import model_to_dict

api = Namespace('genres',
                path='/',
                description='Genre API', )

genre_model = api.model('Genre', {
    'genreId': fields.String(),
    'title': fields.String(),
})

genre_schema = GenreSchema()
genres_many_schema = GenreSchema(many=True)


@api.route('/genre/<genreId>', endpoint='genre_by_id')  # noqa: E501
class GenreResource(Resource):  # type: ignore

    @api.marshal_with(genre_model)
    @api.doc(id='get-genre-by-id', responses={401: 'Unauthorised', 404: 'Not Found'})  # noqa: E501
    def get(self, genreId):  # type: ignore
        result: Optional[Genre] = Genre.query.filter_by(genre_id=genreId).first()  # noqa: E501
        if result is None:
            abort(404)
        return python_dict_to_json_dict(model_to_dict(result))

    @api.doc(id='delete-genre-by-id', responses={401: 'Unauthorised', 404: 'Not Found'})
    def delete(self, genreId):  # type: ignore
        result: Optional[Genre] = Genre.query.filter_by(genre_id=genreId).delete()
        if result != 1:
            abort(404)
        db.session.commit()
        return '', 204

    @api.expect(genre_model, validate=False)
    def put(self, genreId):  # type: ignore
        data = json.loads(request.data)
        if type(data) is not dict:
            return abort(400)

        result: Optional[Genre] = Genre.query.filter_by(genre_id=genreId).first()  # noqa: E501

        if 'genreId' not in data:
            data['genreId'] = uuid4(genreId)

        marshmallow_result = genre_schema.load(
            json_dict_to_python_dict(data),
            session=db.session,
            instance=result,
        )
        if marshmallow_result.errors:
            abort(400, python_dict_to_json_dict(marshmallow_result.errors))

        db.session.add(marshmallow_result.data)
        db.session.commit()
        return '', 201

    @api.expect(genre_model, validate=False)
    def patch(self, genreId):  # type: ignore
        data = json.loads(request.data)
        if type(data) is not dict:
            return abort(400)

        result: Optional[Genre] = Genre.query.filter_by(genre_id=genreId).first()

        if result is None:
            abort(404)

        if 'genreId' not in data:
            data['genreId'] = uuid4(genreId)

        python_dict = json_dict_to_python_dict(data)
        [setattr(result, k, v) for k, v in python_dict.items()]

        db.session.add(result)
        db.session.commit()


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
