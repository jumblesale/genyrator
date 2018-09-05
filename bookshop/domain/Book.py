from bookshop.domain.types import DomainModel, Relationship


from bookshop.sqlalchemy.model.Author import Author
from bookshop.sqlalchemy.model.Review import Review
from bookshop.sqlalchemy.model.Genre import Genre

book = DomainModel(
    external_identifier_map={
        'author_uuid': Relationship(
            sqlalchemy_model_class=Author,
            target_name='author',
            target_identifier_column='author_uuid',
            source_foreign_key_column='author_id',
            lazy=True,
            nullable=False,
        ),
    },
    identifier_column_name='book_id',
    relationship_keys=[
        'author',
        'review',
        'genre',
    ],
    property_keys=[
        'book_id',
        'name',
        'rating',
        'author_id',
        'published',
        'created',
    ],
    json_translation_map={
        'book_id': 'id',
        'author_uuid': 'author_id',
        'review_uuid': 'review_id',
        'genre_uuid': 'genre_id',
    }
)
