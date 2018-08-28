from marshmallow_sqlalchemy import ModelSchema
from bookshop.sqlalchemy.model import (
    Book,
    Author,
    Review,
    Genre,
    BookGenre,
)


class BookSchema(ModelSchema):
    class Meta:
        include_fk = True
        model = Book


class AuthorSchema(ModelSchema):
    class Meta:
        include_fk = True
        model = Author


class ReviewSchema(ModelSchema):
    class Meta:
        include_fk = True
        model = Review


class GenreSchema(ModelSchema):
    class Meta:
        include_fk = True
        model = Genre


class BookGenreSchema(ModelSchema):
    class Meta:
        include_fk = True
        model = BookGenre
