from bookshop.domain.types import DomainModel, Relationship


from bookshop.sqlalchemy.model.Book import Book

author = DomainModel(
    relationship_map={
    },
    identifier_column_name='author_id',
)
