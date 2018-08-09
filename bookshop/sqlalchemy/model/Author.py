from bookshop.sqlalchemy import db
from datetime import datetime
from sqlalchemy import UniqueConstraint


class Author(db.Model):  # type: ignore
    id =        db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.String, index=True, nullable=False)
    name =      db.Column(db.String, index=True, nullable=False)

    __table_args__ = (UniqueConstraint('author_id', ), )

