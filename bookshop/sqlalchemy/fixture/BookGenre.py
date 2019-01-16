import factory

from bookshop.sqlalchemy import db
from bookshop.sqlalchemy.model.BookGenre import BookGenre


class BookGenreFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = BookGenre
        sqlalchemy_session = db.session

    book_genre_id = factory.Faker('uuid4')
