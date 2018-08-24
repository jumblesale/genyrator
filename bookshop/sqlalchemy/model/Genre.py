from bookshop.sqlalchemy import db
from sqlalchemy_utils import UUIDType
from sqlalchemy import UniqueConstraint


class Genre(db.Model):  # type: ignore
    id =       db.Column(db.Integer, primary_key=True)  # noqa: E501
    genre_id = db.Column(UUIDType, index=True, nullable=False)  # noqa: E501
    title =    db.Column(db.String, nullable=True)  # noqa: E501

    __table_args__ = (UniqueConstraint('genre_id', ), )
