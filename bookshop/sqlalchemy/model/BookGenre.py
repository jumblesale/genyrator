from sqlalchemy_utils import UUIDType
from sqlalchemy import UniqueConstraint
from sqlalchemy.types import JSON as JSONType

# Available for custom sqlalchemy_options
import datetime
from sqlalchemy import text, func

from bookshop.sqlalchemy import db
from bookshop.sqlalchemy.model.types import BigIntegerVariantType


class BookGenre(db.Model):  # type: ignore
    # Properties
    id =            db.Column(BigIntegerVariantType, primary_key=True, autoincrement=True)  # noqa: E501
    book_genre_id = db.Column(UUIDType, index=True, nullable=False)  # noqa: E501
    book_id =       db.Column(db.BigInteger, db.ForeignKey('book.id'), nullable=True)  # noqa: E501
    genre_id =      db.Column(db.BigInteger, db.ForeignKey('genre.id'), nullable=True)  # noqa: E501

    # Relationships
    book = db.relationship(
        'Book',
        lazy=False,
        uselist=False,
        foreign_keys=[book_id],
    )
    genre = db.relationship(
        'Genre',
        lazy=False,
        uselist=False,
        foreign_keys=[genre_id],
    )

    __table_args__ = (UniqueConstraint('book_genre_id', ), )
