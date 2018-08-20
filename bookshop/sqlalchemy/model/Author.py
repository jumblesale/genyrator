from bookshop.sqlalchemy import db
from sqlalchemy_utils import UUIDType
from sqlalchemy import UniqueConstraint


class Author(db.Model):  # type: ignore
    id =        db.Column(db.Integer, primary_key=True)  # noqa: E501
    author_id = db.Column(UUIDType, index=True, nullable=False)  # noqa: E501
    name =      db.Column(db.String, index=True, nullable=False)  # noqa: E501
    book =      db.relationship(
        'Book',
        lazy=False,
        uselist=True
    )

    __table_args__ = (UniqueConstraint('author_id', ), )
