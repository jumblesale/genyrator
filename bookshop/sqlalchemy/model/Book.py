from bookshop.sqlalchemy import db
from datetime import datetime
from sqlalchemy import UniqueConstraint


class Book(db.Model):  # type: ignore
    id =      db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.String, index=True, nullable=False)
    name =    db.Column(db.String, index=True, nullable=False)
    rating =  db.Column(db.BigInteger, index=True, nullable=False)
    author =  db.relationship('Author', lazy=False, uselist=False)

    __table_args__ = (UniqueConstraint('book_id', ), )

