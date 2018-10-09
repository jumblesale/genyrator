from sqlalchemy_utils import UUIDType
from sqlalchemy import UniqueConstraint

from bookshop.sqlalchemy import db
from bookshop.sqlalchemy.model.types import BigIntegerVariantType


class Author(db.Model):  # type: ignore
    id =                  db.Column(BigIntegerVariantType, primary_key=True, autoincrement=True)  # noqa: E501
    author_id =           db.Column(UUIDType, index=True, nullable=False)  # noqa: E501
    name =                db.Column(db.String, index=True, nullable=False)  # noqa: E501
    favourite_author_id = db.Column(db.BigInteger, db.ForeignKey('author.id'), nullable=True)  # noqa: E501
    hated_author_id =     db.Column(db.BigInteger, db.ForeignKey('author.id'), nullable=True)  # noqa: E501
    books =               db.relationship(
        'Book',
        lazy=False,
        uselist=True,
        foreign_keys='Book.author_id',
    )
    favourite_book =      db.relationship(
        'Book',
        lazy=False,
        uselist=False,
        foreign_keys='Book.author_id',
    )
    collaborations =      db.relationship(
        'Book',
        lazy=False,
        uselist=True,
        foreign_keys='Book.collaborator_id',
    )

    __table_args__ = (UniqueConstraint('author_id', ), )
