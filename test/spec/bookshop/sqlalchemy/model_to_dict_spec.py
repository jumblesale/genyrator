from expects import expect, have_keys
from mamba import description, it
from sqlalchemy.orm import joinedload

from bookshop import app
from bookshop.sqlalchemy.model import Book, Author
from bookshop.sqlalchemy.model_to_dict import model_to_dict
from bookshop import db

BOOK_ID = '1'

author_model = Author(author_id=3, name='orwell', )
author_dict = {
    "authorId": '3',
    "name": 'orwell',
}
book_model = Book(book_id=BOOK_ID, name='animal farm', rating=4.1, author_id=3)
book_dict = {
    "bookId": BOOK_ID,
    "name": 'animal farm',
    "rating": 4.1,
    "authorId": '3',
}

with app.app_context():
    db.drop_all()
    db.create_all()
    db.session.add(author_model)
    db.session.add(book_model)
    db.session.commit()

with description('model_to_dict') as self:
    with it('converts a flat model into a dict'):
        with app.app_context():
            retrieved_book = Book.query.filter_by(book_id=BOOK_ID).first()
        result = model_to_dict(model=retrieved_book)
        expect(result).to(have_keys(**book_dict))

    with it('converts a singly-nested relationship'):
        with app.app_context():
            retrieved_book = Book.query.\
                filter_by(book_id=BOOK_ID).\
                options(joinedload('author')).\
                first()
        result = model_to_dict(model=retrieved_book, paths=['author'])
        expect(result).to(have_keys(**book_dict))
        expect(result['author']).to(have_keys(**author_dict))
