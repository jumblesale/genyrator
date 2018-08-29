from sqlalchemy_utils import UUIDType
from sqlalchemy import UniqueConstraint

from bookshop.sqlalchemy import db
from bookshop.sqlalchemy.model.types import BigIntegerVariantType


class BookGenre(db.Model):  # type: ignore
    id =            db.Column(BigIntegerVariantType, primary_key=True, autoincrement=True)  # noqa: E501
    book_genre_id = db.Column(UUIDType, index=True, nullable=False)  # noqa: E501
    book_id =       db.Column(db.BigInteger, db.ForeignKey('book.id'), nullable=True)  # noqa: E501
    genre_id =      db.Column(db.BigInteger, db.ForeignKey('genre.id'), nullable=True)  # noqa: E501
    book =          db.relationship(
        'Book',
        lazy=False,
        uselist=False
    )
    genre =         db.relationship(
        'Genre',
        lazy=False,
        uselist=False
    )

    __table_args__ = (UniqueConstraint('book_genre_id', ), )
