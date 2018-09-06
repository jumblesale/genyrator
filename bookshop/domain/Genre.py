from bookshop.domain.types import DomainModel, Relationship


from bookshop.sqlalchemy.model.Book import Book

genre = DomainModel(
    external_identifier_map={
    },
    identifier_column_name='genre_id',
    relationship_keys=[
        'book',
    ],
    property_keys=[
        'genre_id',
        'title',
    ],
    json_translation_map={
        'genre_id': 'id',
        'book_id': '',
    }
)
