from bookshop.sqlalchemy import db
from sqlalchemy_utils import UUIDType
from sqlalchemy import UniqueConstraint


class Book(db.Model):  # type: ignore
    id =        db.Column(db.Integer, primary_key=True)  # noqa: E501
    book_id =   db.Column(UUIDType, index=True, nullable=False)  # noqa: E501
    name =      db.Column(db.String, index=True, nullable=False)  # noqa: E501
    rating =    db.Column(db.BigInteger, index=True, nullable=False)  # noqa: E501
    author_id = db.Column(db.String, db.ForeignKey('author.author_id'), nullable=True)  # noqa: E501
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
