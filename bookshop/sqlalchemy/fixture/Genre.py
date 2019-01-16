import factory

from bookshop.sqlalchemy import db
from bookshop.sqlalchemy.model.Genre import Genre


class GenreFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Genre
        sqlalchemy_session = db.session

    genre_id = factory.Faker('uuid4')
