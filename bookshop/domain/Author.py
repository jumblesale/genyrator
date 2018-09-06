from bookshop.domain.types import DomainModel, Relationship


from bookshop.sqlalchemy.model.Book import Book
from bookshop.sqlalchemy.model.Book import Book

author = DomainModel(
    external_identifier_map={
        'book_id': Relationship(
            sqlalchemy_model_class=Book,
            target_name='book',
            target_identifier_column='book_id',
            source_foreign_key_column='None',
            lazy=True,
            nullable=False,
        ),
    },
    identifier_column_name='author_id',
    relationship_keys=[
        'books',
        'favourite_book',
    ],
    property_keys=[
        'author_id',
        'name',
    ],
    json_translation_map={
        'author_id': 'id',
        'book_id': 'None',
        'book_id': 'None',
    }
)
