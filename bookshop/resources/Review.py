import json
from typing import Optional

from flask import request, abort, url_for
from flask_restplus import Resource, fields, Namespace


from bookshop.core.convert_dict import (
    python_dict_to_json_dict, json_dict_to_python_dict
)
from bookshop.sqlalchemy import db
from bookshop.sqlalchemy.model import Review
from bookshop.sqlalchemy.convert_properties import (
    convert_properties_to_sqlalchemy_properties, convert_sqlalchemy_properties_to_dict_properties
)
from bookshop.sqlalchemy.join_entities import create_joined_entity_map
from bookshop.schema import ReviewSchema
from bookshop.sqlalchemy.model_to_dict import model_to_dict
from bookshop.sqlalchemy.convert_dict_to_marshmallow_result import convert_dict_to_marshmallow_result
from bookshop.domain.Review import review as review_domain_model

api = Namespace('reviews',
                path='/',
                description='Review API', )

review_model = api.model('Review', {
    'id': fields.String(attribute='reviewId'),
    'text': fields.String(),
    'bookId': fields.String(),
})

review_schema = ReviewSchema()
reviews_many_schema = ReviewSchema(many=True)


@api.route('/review/<reviewId>', endpoint='review_by_id')  # noqa: E501
class ReviewResource(Resource):  # type: ignore
    @api.doc(id='get-review-by-id', responses={401: 'Unauthorised', 404: 'Not Found'})  # noqa: E501
    def get(self, reviewId):  # type: ignore
        result: Optional[Review] = Review.query.filter_by(review_id=reviewId).first()  # noqa: E501
        if result is None:
            abort(404)
        response = model_to_dict(
            result,
        ), 200
        return response

    @api.doc(id='delete-review-by-id', responses={401: 'Unauthorised', 404: 'Not Found'})
    def delete(self, reviewId):  # type: ignore
        result: Optional[Review] = Review.query.filter_by(review_id=reviewId).delete()
        if result != 1:
            abort(404)
        db.session.commit()
        return '', 204

    @api.expect(review_model, validate=False)
    @api.marshal_with(review_model)
    def put(self, reviewId):  # type: ignore
        data = json.loads(request.data)
        if type(data) is not dict:
            return abort(400)

        if 'id' not in data:
            data['id'] = reviewId

        result: Optional[Review] = Review.query.filter_by(review_id=reviewId).first()  # noqa: E501

        marshmallow_schema_or_errors = convert_dict_to_marshmallow_result(
            data=json_dict_to_python_dict(model_to_dict(sqlalchemy_model=result)),
            identifier=reviewId,
            identifier_column='review_id',
            domain_model=review_domain_model,
            sqlalchemy_model=Review,
            schema=review_schema,
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

    @api.expect(review_model, validate=False)
    def patch(self, reviewId):  # type: ignore
        result: Optional[Review] = Review.query.filter_by(review_id=reviewId).first()  # noqa: E501

        if result is None:
            abort(404)

        data = json.loads(request.data)

        if type(data) is not dict:
            return abort(400)

        marshmallow_schema_or_errors = convert_dict_to_marshmallow_result(
            data=json_dict_to_python_dict(model_to_dict(result)),
            identifier=reviewId,
            identifier_column='review_id',
            domain_model=review_domain_model,
            sqlalchemy_model=Review,
            schema=review_schema,
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
    

@api.route('/reviews', endpoint='reviews')  # noqa: E501
class ManyReviewResource(Resource):  # type: ignore
    def get(self):
        result = Review.query.all()
        urls = [
            url_for(
                'review_by_id',
                reviewId=x.review_id
            )
            for x in result
        ]
        return {"links": urls}

    def post(self):  # type: ignore
        ...
