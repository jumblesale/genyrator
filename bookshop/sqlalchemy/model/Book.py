from sqlalchemy_utils import UUIDType
from sqlalchemy import UniqueConstraint

from bookshop.sqlalchemy import db
from bookshop.sqlalchemy.model.types import BigIntegerVariantType


class Book(db.Model):  # type: ignore
    id =        db.Column(BigIntegerVariantType, primary_key=True, autoincrement=True)  # noqa: E501
    book_id =   db.Column(UUIDType, index=True, nullable=False)  # noqa: E501
    name =      db.Column(db.String, index=True, nullable=False)  # noqa: E501
    rating =    db.Column(db.Float, index=True, nullable=False)  # noqa: E501
    author_id = db.Column(db.BigInteger, db.ForeignKey('author.id'), nullable=True)  # noqa: E501
    published = db.Column(db.Date, nullable=True)  # noqa: E501
    created =   db.Column(db.DateTime, nullable=True)  # noqa: E501
    author =    db.relationship(
        'Author',
        lazy=False,
        uselist=False
    )
    review =    db.relationship(
        'Review',
        lazy=False,
        uselist=True
    )
    genre =     db.relationship(
        'Genre',
        lazy=False,
        uselist=False,
        secondary='book_genre'
    )

    __table_args__ = (UniqueConstraint('book_id', ), )
