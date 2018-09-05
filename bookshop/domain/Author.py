from bookshop.domain.types import DomainModel, Relationship


from bookshop.sqlalchemy.model.Book import Book
from bookshop.sqlalchemy.model.Book import Book

author = DomainModel(
    relationship_map={
        'book_id': Relationship(
            target=Book,
            target_name='book',
            target_identifier_column='book_id',
            source_foreign_key_column='favourite_book_id',
            lazy=True,
        ),
    },
    identifier_column_name='author_id',
    relationship_keys=[
        'books',
        'favourite_book',
    ],
)
