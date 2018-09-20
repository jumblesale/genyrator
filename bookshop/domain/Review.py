from bookshop.domain.types import DomainModel, Relationship


from bookshop.sqlalchemy.model.Book import Book

review = DomainModel(
    external_identifier_map={
        'book_id': Relationship(
            sqlalchemy_model_class=Book,
            target_name='book',
            target_identifier_column='book_id',
            source_foreign_key_column='book_id',
            lazy=False,
            nullable=False,
        ),
    },
    identifier_column_name='review_id',
    relationship_keys=[
        'book',
    ],
    property_keys=[
        'review_id',
        'text',
        'book_id',
    ],
    json_translation_map={
        'review_id': 'id',
        'book_id': 'book',
    },
    eager_relationships=[
        'book',
    ],
)
