from typing import List

from genyrator import create_entity, create_column, TypeOption, create_identifier_column, create_relationship, \
    JoinOption
from genyrator.entities.Entity import all_operations, Entity, create_api_path
from genyrator.entities.Schema import create_schema, Schema

book_entity = create_entity(
    class_name='Book',
    identifier_column=create_identifier_column(
        name='book_id', type_option=TypeOption.uuid,
    ),
    columns=[
        create_column(
            name='name', type_option=TypeOption.string,
            index=True, nullable=False,
        ),
        create_column(
            name='rating', type_option=TypeOption.int,
            index=True, nullable=False,
        ),
        create_column(
            name='author_id', type_option=TypeOption.string,
            foreign_key_relationship='author.author_id'
        ),
    ],
    relationships=[
        create_relationship(
            target_entity_class_name='Author',
            nullable=False,
            lazy=False,
            join=JoinOption.to_one,
        ),
        create_relationship(
            target_entity_class_name='Review',
            nullable=False,
            lazy=False,
            join=JoinOption.to_many,
        ),
        create_relationship(
            target_entity_class_name='Genre',
            nullable=False,
            lazy=False,
            join=JoinOption.to_one,
            join_table='book_genre',
            property_name='genre',
        ),
    ],
    operations=all_operations,
    api_paths=[
        create_api_path(
            joined_entities=[
                'genre',
            ],
            route='genres',
        ),
    ],
)

author_entity = create_entity(
    class_name='Author',
    identifier_column=create_identifier_column(
        'author_id', TypeOption.uuid,
    ),
    columns=[
        create_column(
            name='name', type_option=TypeOption.string,
            index=True, nullable=False,
        ),
    ],
    relationships=[
        create_relationship(
            target_entity_class_name='Book',
            nullable=False,
            lazy=False,
            join=JoinOption.to_many,
        )
    ],
    api_paths=[
        create_api_path(
            joined_entities=['Author', 'Book', 'Review'],
            route='books/reviews',
        ),
    ],
)

review_entity = create_entity(
    class_name='Review',
    identifier_column=create_identifier_column(
        name='review_id', type_option=TypeOption.uuid,
    ),
    columns=[
        create_column(
            name='text', type_option=TypeOption.string,
            index=True, nullable=False,
        ),
        create_column(
            name='book_id', type_option=TypeOption.string,
            foreign_key_relationship='book.book_id'
        )
    ],
    relationships=[
        create_relationship(
            target_entity_class_name='Book',
            nullable=False,
            lazy=False,
            join=JoinOption.to_one,
        )
    ],
    operations=all_operations,
)

genre_entity = create_entity(
    class_name='Genre',
    identifier_column=create_identifier_column('genre_id', TypeOption.uuid),
    columns=[
        create_column(
            name='title',
            type_option=TypeOption.string,
        ),
    ],
    relationships=[
        create_relationship(
            target_entity_class_name='Book', nullable=True, lazy=False, join=JoinOption.to_many, join_table='book_genre'
        ),
    ],
)

book_genre_entity = create_entity(
    class_name='BookGenre',
    identifier_column=create_identifier_column('book_genre_id', TypeOption.uuid),
    columns=[
        create_column('book_id',  type_option=TypeOption.int, foreign_key_relationship='book.book_id'),
        create_column('genre_id', type_option=TypeOption.int, foreign_key_relationship='genre.genre_id'),
    ],
    relationships=[
        create_relationship('Book',  nullable=False, lazy=False, join=JoinOption.to_one),
        create_relationship('Genre', nullable=False, lazy=False, join=JoinOption.to_one),
    ],
)


def write_app(schema: Schema):
    schema.write_files()


def create_bookshop_schema(entities: List[Entity]) -> Schema:
    schema = create_schema(
        module_name='bookshop',
        entities=entities,
    )
    return schema


if __name__ == '__main__':
    schema = create_bookshop_schema([
        book_entity, author_entity, review_entity, genre_entity, book_genre_entity
    ])
    write_app(schema)
