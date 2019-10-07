from sqlalchemy_utils import UUIDType
from sqlalchemy import UniqueConstraint
from sqlalchemy.types import JSON as JSONType

# Available for custom sqlalchemy_options
import datetime
from sqlalchemy import text, func

from bookshop.sqlalchemy import db
from bookshop.sqlalchemy.model.types import BigIntegerVariantType


class Book(db.Model):  # type: ignore
    # Properties
    id =              db.Column(BigIntegerVariantType, primary_key=True, autoincrement=True)  # noqa: E501
    book_id =         db.Column(UUIDType, index=True, nullable=False)  # noqa: E501
    name =            db.Column(db.String, index=True, nullable=False)  # noqa: E501
    rating =          db.Column(db.Float, index=True, nullable=False)  # noqa: E501
    author_id =       db.Column(db.BigInteger, db.ForeignKey('author.id'), nullable=True)  # noqa: E501
    collaborator_id = db.Column(db.BigInteger, db.ForeignKey('author.id'), nullable=True)  # noqa: E501
    published =       db.Column(db.Date, nullable=True)  # noqa: E501
    created =         db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'), nullable=True)  # noqa: E501
    updated =         db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=True)  # noqa: E501

    # Relationships
    author = db.relationship(
        'Author',
        lazy=False,
        uselist=False,
        foreign_keys=[author_id],
    )
    collaborator = db.relationship(
        'Author',
        lazy=False,
        uselist=False,
        foreign_keys=[collaborator_id],
    )
    reviews = db.relationship(
        'Review',
        lazy=True,
        uselist=True,
    )
    genre = db.relationship(
        'Genre',
        lazy=False,
        uselist=False,
        secondary='book_genre',
    )
    related_books = db.relationship(
        'Book',
        lazy=True,
        uselist=True,
        secondary='related_book',
        primaryjoin='Book.id==RelatedBook.book1_id',
        secondaryjoin='Book.id==RelatedBook.book2_id',
    )

    __table_args__ = (UniqueConstraint('book_id', ), )
