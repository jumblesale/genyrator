import factory
import uuid

from bookshop.sqlalchemy import db
from bookshop.sqlalchemy.model.Book import Book


class BookFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Book
        sqlalchemy_session = db.session

    book_id = factory.Faker('uuid4')
