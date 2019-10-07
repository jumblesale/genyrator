from sqlalchemy_utils import UUIDType
from sqlalchemy import UniqueConstraint
from sqlalchemy.types import JSON as JSONType

# Available for custom sqlalchemy_options
import datetime
from sqlalchemy import text, func

from bookshop.sqlalchemy import db
from bookshop.sqlalchemy.model.types import BigIntegerVariantType


class Genre(db.Model):  # type: ignore
    # Properties
    id =       db.Column(BigIntegerVariantType, primary_key=True, autoincrement=True)  # noqa: E501
    genre_id = db.Column(UUIDType, index=True, nullable=False)  # noqa: E501
    title =    db.Column(db.String, nullable=True)  # noqa: E501

    # Relationships
    book = db.relationship(
        'Book',
        lazy=False,
        uselist=True,
        secondary='book_genre',
    )

    __table_args__ = (UniqueConstraint('genre_id', ), )
