from bookshop.domain.types import DomainModel, Relationship


from bookshop.sqlalchemy.model.Book import Book
from bookshop.sqlalchemy.model.Genre import Genre

book_genre = DomainModel(
    relationship_map={
        'book_id': Relationship(
            target=Book,
            target_identifier_column='book_id',
            lazy=True,
        ),
        'genre_id': Relationship(
            target=Genre,
            target_identifier_column='genre_id',
            lazy=True,
        ),
    },
    identifier_column_name='book_genre_id',
)
