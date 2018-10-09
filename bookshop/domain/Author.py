from bookshop.domain.types import DomainModel, Relationship


from bookshop.sqlalchemy.model.Book import Book
from bookshop.sqlalchemy.model.Author import Author

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
        'favourite_author_id': Relationship(
            sqlalchemy_model_class=Author,
            target_name='author',
            target_identifier_column='author_id',
            source_foreign_key_column='favourite_author_id',
            lazy=True,
            nullable=True,
        ),
        'hated_author_id': Relationship(
            sqlalchemy_model_class=Author,
            target_name='author',
            target_identifier_column='author_id',
            source_foreign_key_column='hated_author_id',
            lazy=True,
            nullable=True,
        ),
    },
    identifier_column_name='author_id',
    relationship_keys=[
        'books',
        'favourite_book',
        'collaborations',
        'favourite_of',
        'favourite_author',
        'hated_by',
        'hated_author',
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
        'favourite_author_id': 'favourite_author',
        'hated_author_id': 'hated_author',
    },
    eager_relationships=[
        'books',
        'favourite_book',
        'collaborations',
    ],
)
