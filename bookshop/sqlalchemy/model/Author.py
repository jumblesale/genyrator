from sqlalchemy_utils import UUIDType
from sqlalchemy import UniqueConstraint

from bookshop.sqlalchemy import db
from bookshop.sqlalchemy.model.types import BigIntegerVariantType


class Author(db.Model):  # type: ignore
    id =        db.Column(BigIntegerVariantType, primary_key=True, autoincrement=True)  # noqa: E501
    author_id = db.Column(UUIDType, index=True, nullable=False)  # noqa: E501
    name =      db.Column(db.String, index=True, nullable=False)  # noqa: E501
    book =      db.relationship(
        'Book',
        lazy=False,
        uselist=True
    )

    __table_args__ = (UniqueConstraint('author_id', ), )
