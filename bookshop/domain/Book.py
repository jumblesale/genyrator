from bookshop.domain.types import DomainModel, Relationship


from bookshop.sqlalchemy.model.Author import Author
from bookshop.sqlalchemy.model.Review import Review
from bookshop.sqlalchemy.model.Genre import Genre

book = DomainModel(
    relationship_map={
        'author_id': Relationship(
            target=Author,
            target_identifier_column='author_id',
            lazy=True,
        ),
        'review_id': Relationship(
            target=Review,
            target_identifier_column='review_id',
            lazy=True,
        ),
    },
    identifier_column_name='book_id',
)
