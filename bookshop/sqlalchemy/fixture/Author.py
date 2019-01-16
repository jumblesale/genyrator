import factory

from bookshop.sqlalchemy import db
from bookshop.sqlalchemy.model.Author import Author


class AuthorFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Author
        sqlalchemy_session = db.session

    author_id = factory.Faker('uuid4')
    name = factory.Faker('pystr')
