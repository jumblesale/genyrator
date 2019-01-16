import factory

from bookshop.sqlalchemy import db
from bookshop.sqlalchemy.model.Book import Book


class BookFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Book
        sqlalchemy_session = db.session

    book_id = factory.Faker('uuid4')
    name = factory.Faker('pystr')
    rating = factory.Faker('pyfloat')
