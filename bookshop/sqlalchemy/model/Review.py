from bookshop.sqlalchemy import db
from sqlalchemy import UniqueConstraint


class Review(db.Model):  # type: ignore
    id =        db.Column(db.Integer, primary_key=True)  # noqa: E501
    review_id = db.Column(db.String, index=True, nullable=False)  # noqa: E501
    text =      db.Column(db.String, index=True, nullable=False)  # noqa: E501
    book_id =   db.Column(db.String, db.ForeignKey('book.book_id'), nullable=True)  # noqa: E501
    book =      db.relationship(
        'Book',
        lazy=False,
        uselist=False
    )

    __table_args__ = (UniqueConstraint('review_id', ), )
