import factory
import uuid

from bookshop.sqlalchemy import db
from bookshop.sqlalchemy.model.RelatedBook import RelatedBook


class RelatedBookFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = RelatedBook
        sqlalchemy_session = db.session

    related_book_uuid = factory.Faker('uuid4')
