from sqlalchemy_utils import UUIDType, JSONType
from sqlalchemy import UniqueConstraint

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
    created =         db.Column(db.DateTime, nullable=True)  # noqa: E501

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
