from bookshop.domain.types import DomainModel, Relationship


from bookshop.sqlalchemy.model.Author import Author
from bookshop.sqlalchemy.model.Genre import Genre
from bookshop.sqlalchemy.model.Review import Review

book = DomainModel(
    external_identifier_map={
        'author_id': Relationship(
            sqlalchemy_model_class=Author,
            target_name='author',
            target_identifier_column='author_id',
            source_foreign_key_column='author_id',
            lazy=False,
            nullable=False,
        ),
        'collaborator_id': Relationship(
            sqlalchemy_model_class=Author,
            target_name='author',
            target_identifier_column='author_id',
            source_foreign_key_column='collaborator_id',
            lazy=False,
            nullable=True,
        ),
    },
    identifier_column_name='book_id',
    relationship_keys=[
        'author',
        'collaborator',
        'reviews',
        'genre',
    ],
    property_keys=[
        'book_id',
        'name',
        'rating',
        'author_id',
        'collaborator_id',
        'published',
        'created',
    ],
    json_translation_map={
        'book_id': 'id',
        'author_id': 'author',
        'collaborator_id': 'collaborator',
    },
    eager_relationships=[
        'author',
        'collaborator',
        'genre',
    ],
)
