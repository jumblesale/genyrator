import factory

from bookshop.sqlalchemy import db as db
from bookshop.sqlalchemy.model.Review import Review


class ReviewFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Review
        sqlalchemy_session = db.session

    review_id = factory.Faker('uuid4')
    text = factory.Faker('pystr')
