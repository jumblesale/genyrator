from bookshop.domain.types import DomainModel, Relationship


from bookshop.sqlalchemy.model.Book import Book

related_book = DomainModel(
    external_identifier_map={
        'book1_id': Relationship(
            sqlalchemy_model_class=Book,
            target_name='book',
            target_identifier_column='book_id',
            source_foreign_key_column='book1_id',
            lazy=False,
            nullable=False,
        ),
        'book2_id': Relationship(
            sqlalchemy_model_class=Book,
            target_name='book',
            target_identifier_column='book_id',
            source_foreign_key_column='book2_id',
            lazy=False,
            nullable=False,
        ),
    },
    identifier_column_name='related_book_uuid',
    relationship_keys=[
        'book1',
        'book2',
    ],
    property_keys=[
        'related_book_uuid',
        'book1_id',
        'book2_id',
    ],
    json_translation_map={
        'related_book_uuid': 'id',
        'book1_id': 'book1',
        'book2_id': 'book2',
    },
    eager_relationships=[
        'book1',
        'book2',
    ],
)
