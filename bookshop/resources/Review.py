import json
from flask import request, abort, url_for
from flask_restplus import Resource, fields, Namespace

from typing import Optional
from uuid import UUID

from bookshop.core.convert_dict import (
    python_dict_to_json_dict, json_dict_to_python_dict
)
from bookshop.sqlalchemy import db
from bookshop.sqlalchemy.model import Review
from bookshop.schema import ReviewSchema
from bookshop.sqlalchemy.model_to_dict import model_to_dict

api = Namespace('reviews',
                path='/',
                description='Review API', )

review_model = api.model('Review', {
    'reviewId': fields.String(),
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
        return python_dict_to_json_dict(model_to_dict(result))

    @api.doc(id='delete-review-by-id', responses={401: 'Unauthorised', 404: 'Not Found'})
    def delete(self, reviewId):  # type: ignore
        result: Optional[Review] = Review.query.filter_by(review_id=reviewId).delete()
        if result != 1:
            abort(404)
        db.session.commit()
        return '', 204

    @api.expect(review_model, validate=False)
    def put(self, reviewId):  # type: ignore
        data = json.loads(request.data)
        if type(data) is not dict:
            return abort(400)

        result: Optional[Review] = Review.query.filter_by(review_id=reviewId).first()  # noqa: E501

        if 'reviewId' not in data:
            data['reviewId'] = UUID(reviewId)

        marshmallow_result = review_schema.load(
            json_dict_to_python_dict(data),
            session=db.session,
            instance=result,
        )
        if marshmallow_result.errors:
            abort(400, python_dict_to_json_dict(marshmallow_result.errors))

        db.session.add(marshmallow_result.data)
        db.session.commit()
        return '', 201

    @api.expect(review_model, validate=False)
    def patch(self, reviewId):  # type: ignore
        data = json.loads(request.data)
        if type(data) is not dict:
            return abort(400)

        result: Optional[Review] = Review.query.filter_by(review_id=reviewId).first()

        if result is None:
            abort(404)

        if 'reviewId' not in data:
            data['reviewId'] = UUID(reviewId)

        python_dict = json_dict_to_python_dict(data)
        [setattr(result, k, v) for k, v in python_dict.items()]

        db.session.add(result)
        db.session.commit()


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
