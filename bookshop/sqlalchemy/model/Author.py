from sqlalchemy_utils import UUIDType
from sqlalchemy import UniqueConstraint
from sqlalchemy.types import JSON as JSONType

# Available for custom sqlalchemy_options
import datetime
from sqlalchemy import text, func

from bookshop.sqlalchemy import db
from bookshop.sqlalchemy.model.types import BigIntegerVariantType


class Author(db.Model):  # type: ignore
    # Properties
    id =                  db.Column(BigIntegerVariantType, primary_key=True, autoincrement=True)  # noqa: E501
    author_id =           db.Column(UUIDType, index=True, nullable=False)  # noqa: E501
    name =                db.Column(db.String, index=True, nullable=False)  # noqa: E501
    favourite_author_id = db.Column(db.BigInteger, db.ForeignKey('author.id'), nullable=True)  # noqa: E501
    hated_author_id =     db.Column(db.BigInteger, db.ForeignKey('author.id'), nullable=True)  # noqa: E501

    # Relationships
    books = db.relationship(
        'Book',
        lazy=False,
        uselist=True,
        foreign_keys='Book.author_id',
    )
    favourite_book = db.relationship(
        'Book',
        lazy=False,
        uselist=False,
        foreign_keys='Book.author_id',
    )
    collaborations = db.relationship(
        'Book',
        lazy=False,
        uselist=True,
        foreign_keys='Book.collaborator_id',
    )
    favourite_of = db.relationship(
        'Author',
        lazy=True,
        uselist=True,
        foreign_keys=[favourite_author_id],
    )
    favourite_author = db.relationship(
        'Author',
        lazy=True,
        uselist=False,
        primaryjoin=id==favourite_author_id,
        remote_side=[id],
    )
    hated_by = db.relationship(
        'Author',
        lazy=True,
        uselist=True,
        foreign_keys=[hated_author_id],
    )
    hated_author = db.relationship(
        'Author',
        lazy=True,
        uselist=False,
        primaryjoin=id==hated_author_id,
        remote_side=[id],
    )

    __table_args__ = (UniqueConstraint('author_id', ), )
