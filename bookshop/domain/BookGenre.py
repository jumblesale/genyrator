from bookshop.domain.types import DomainModel, Relationship


from bookshop.sqlalchemy.model.Book import Book
from bookshop.sqlalchemy.model.Genre import Genre

book_genre = DomainModel(
    external_identifier_map={
        'book_id': Relationship(
            sqlalchemy_model_class=Book,
            target_name='book',
            target_identifier_column='book_id',
            source_foreign_key_column='book_id',
            lazy=False,
            nullable=False,
        ),
        'genre_id': Relationship(
            sqlalchemy_model_class=Genre,
            target_name='genre',
            target_identifier_column='genre_id',
            source_foreign_key_column='genre_id',
            lazy=False,
            nullable=False,
        ),
    },
    identifier_column_name='book_genre_id',
    relationship_keys=[
        'book',
        'genre',
    ],
    property_keys=[
        'book_genre_id',
        'book_id',
        'genre_id',
    ],
    json_translation_map={
        'book_genre_id': 'id',
        'book_id': 'book',
        'genre_id': 'genre',
    },
    eager_relationships=[
        'book',
        'genre',
    ],
)
