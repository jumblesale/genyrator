from marshmallow_sqlalchemy import ModelSchema
from bookshop.sqlalchemy.model import *


class BookSchema(ModelSchema):
    class Meta:
        include_fk = True
        model = Book


class AuthorSchema(ModelSchema):
    class Meta:
        include_fk = True
        model = Author

