from bookshop.domain.types import DomainModel, Relationship


from bookshop.sqlalchemy.model.Book import Book
from bookshop.sqlalchemy.model.Book import Book
from bookshop.sqlalchemy.model.Book import Book

author = DomainModel(
    external_identifier_map={
        'book_id': Relationship(
            sqlalchemy_model_class=Book,
            target_name='book',
            target_identifier_column='book_id',
            source_foreign_key_column='None',
            lazy=False,
            nullable=False,
        ),
    },
    identifier_column_name='author_id',
    relationship_keys=[
        'books',
        'favourite_book',
        'collaborations',
    ],
    property_keys=[
        'author_id',
        'name',
        'favourite_author_id',
        'hated_author_id',
    ],
    json_translation_map={
        'author_id': 'id',
        'book_id': 'favourite_book',
    },
    eager_relationships=[
        'books',
        'favourite_book',
        'collaborations',
    ],
)
