from bookshop.domain.types import DomainModel, Relationship


from bookshop.sqlalchemy.model.Book import Book

review = DomainModel(
    relationship_map={
        'book_id': Relationship(
            target=Book,
            target_identifier_column='book_id',
            lazy=True,
        ),
    },
    identifier_column_name='review_id',
)
