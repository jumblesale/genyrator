import datetime
import uuid

from expects import expect, have_keys, have_key, equal
from mamba import description, it
from sqlalchemy.orm import joinedload

from bookshop import app
from bookshop.sqlalchemy.model import Book, Author, Genre, BookGenre
from bookshop.domain.Book import book as book_domain_model
from bookshop.sqlalchemy.model_to_dict import model_to_dict
from bookshop import db

BOOK_UUID =   uuid.uuid4()
AUTHOR_UUID = uuid.uuid4()
GENRE_UUID =  uuid.uuid4()

datetime_now = datetime.datetime.now()
date_now =     datetime.datetime.today()

author_model = Author(id=1, author_id=str(AUTHOR_UUID), name='orwell')
author_dict = {
    "id": str(AUTHOR_UUID),
    "name": 'orwell',
}

book_model = Book(
    id=1,
    book_id=str(BOOK_UUID),
    name='animal farm',
    rating=4.1,
    author_id=1,
    published=date_now,
    created=datetime_now,
)
book_dict = {
    "id": str(BOOK_UUID),
    "name": 'animal farm',
    "rating": 4.1,
    "published": date_now.strftime('%Y-%m-%d'),
    "created": datetime_now.isoformat(),
}

genre_model = Genre(
    id=1,
    genre_id=GENRE_UUID,
    title='genre title',
)
book_genre_model = BookGenre(
    id=1, book_genre_id=uuid.uuid4(),
    book_id=1, genre_id=1,
)

with app.app_context():
    db.drop_all()
    db.create_all()
    db.session.add(author_model)
    db.session.add(book_model)
    db.session.commit()

with description('model_to_dict') as self:
    with it('converts a flat model into a dict'):
        with app.app_context():
            retrieved_book = Book.query.filter_by(book_id=BOOK_UUID).first()
        result = model_to_dict(
            sqlalchemy_model=retrieved_book,
        )
        expect(result).to(have_keys(**book_dict))

    with it('converts a singly-nested relationship'):
        with app.app_context():
            retrieved_book = Book.query.\
                filter_by(book_id=BOOK_UUID).\
                options(joinedload('author')).\
                first()
            result = model_to_dict(
                sqlalchemy_model=retrieved_book,
                paths=['author'],
            )
        expect(result).to(have_keys(**book_dict))
        expect(result['author']).to(have_keys(**author_dict))

    with it('always converts eager relationships'):
        with app.app_context():
            retrieved_book = Book.query.\
                filter_by(book_id=BOOK_UUID).\
                options(joinedload('author')).\
                first()
            result = model_to_dict(
                sqlalchemy_model=retrieved_book
            )
        expect(result).to(have_keys(**book_dict))
        expect(result['author']).to(have_keys(**author_dict))

    with it('gives an empty response when relationship does not exist'):
        book_without_author = Book(
            book_id=str(uuid.uuid4()),
            name='',
            rating=0.2,
        )
        with app.app_context():
            db.session.add(book_without_author)
            db.session.commit()
            retrieved_book = Book.query.\
                filter_by(book_id=book_without_author.book_id).\
                first()
        result = model_to_dict(
            sqlalchemy_model=retrieved_book,
            paths=['author'],
        )
        expect(result).to(have_key('author'))
        expect(result['author']).to(equal(None))

    with it('converts a deeply nested relationship'):
        with app.app_context():
            db.session.add(genre_model)
            db.session.add(book_genre_model)
            db.session.commit()
            retrieved_genre = Book.query. \
                filter_by(id=1). \
                options(joinedload('genre')). \
                first()
            result = model_to_dict(
                sqlalchemy_model=retrieved_genre,
                paths=['genre'],
            )
        expect(result['genre']['id']).to(equal(str(GENRE_UUID)))
