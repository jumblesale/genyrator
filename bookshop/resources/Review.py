import json
from typing import Optional

from flask import request, abort, url_for
from flask_restplus import Resource, fields, Namespace


from bookshop.core.convert_dict import (
    python_dict_to_json_dict, json_dict_to_python_dict
)
from bookshop.sqlalchemy import db
from bookshop.sqlalchemy.model import Review
from bookshop.sqlalchemy.convert_properties import convert_properties_to_sqlalchemy_properties
from bookshop.sqlalchemy.join_entities import create_joined_entity_map
from bookshop.schema import ReviewSchema
from bookshop.sqlalchemy.model_to_dict import model_to_dict
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
    @api.marshal_with(review_model)
    @api.doc(id='get-review-by-id', responses={401: 'Unauthorised', 404: 'Not Found'})  # noqa: E501
    def get(self, reviewId):  # type: ignore
        result: Optional[Review] = Review.query.filter_by(review_id=reviewId).first()  # noqa: E501
        if result is None:
            abort(404)
        return model_to_dict(
            result,
            review_domain_model,
        ), 200

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

        result: Optional[Review] = Review.query.filter_by(review_id=reviewId).first()  # noqa: E501

        joined_entities = create_joined_entity_map(
            review_domain_model,
            data,
        )

        data = convert_properties_to_sqlalchemy_properties(
            review_domain_model,
            joined_entities,
            json_dict_to_python_dict(data),
        )

        marshmallow_result = review_schema.load(
            json_dict_to_python_dict(data),
            session=db.session,
            instance=result,
        )
        if marshmallow_result.errors:
            abort(400, python_dict_to_json_dict(marshmallow_result.errors))

        db.session.add(marshmallow_result.data)
        db.session.commit()

        return model_to_dict(
            marshmallow_result.data,
            review_domain_model,
        ), 201

    @api.expect(review_model, validate=False)
    def patch(self, reviewId):  # type: ignore
        ...



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
