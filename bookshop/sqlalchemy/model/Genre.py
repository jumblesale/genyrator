from sqlalchemy_utils import UUIDType
from sqlalchemy import UniqueConstraint
from sqlalchemy.types import JSON as JSONType

from bookshop.sqlalchemy import db as db
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
