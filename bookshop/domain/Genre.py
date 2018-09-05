from bookshop.domain.types import DomainModel, Relationship


from bookshop.sqlalchemy.model.Book import Book

genre = DomainModel(
    relationship_map={
    },
    identifier_column_name='genre_id',
    relationship_keys=[
        'book',
    ],
)
