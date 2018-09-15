from typing import List

from genyrator import create_entity, create_column, TypeOption, create_identifier_column, create_relationship, \
    JoinOption
from genyrator.entities.Column import ForeignKeyRelationship
from genyrator.entities.Entity import all_operations, Entity, create_api_path
from genyrator.entities.Schema import create_schema, Schema

book_entity = create_entity(
    class_name='Book',
    identifier_column=create_identifier_column(
        name='book_id', type_option=TypeOption.UUID,
    ),
    columns=[
        create_column(
            name='name', type_option=TypeOption.string,
            index=True, nullable=False,
        ),
        create_column(
            name='rating', type_option=TypeOption.float,
            index=True, nullable=False,
        ),
        create_column(
            name='author_id', type_option=TypeOption.int,
            foreign_key_relationship=ForeignKeyRelationship(
                target_entity='author',
                target_entity_identifier_column_type=TypeOption.UUID,
            ),
        ),
        create_column(
            name='published', type_option=TypeOption.date,
            # alias='date_published',
        ),
        create_column(
            name='created', type_option=TypeOption.datetime,
        ),
    ],
    relationships=[
        create_relationship(
            source_foreign_key_column_name='author_id',
            source_identifier_column_name='book_uuid',
            target_identifier_column_name='author_uuid',
            target_entity_class_name='Author',
            nullable=False,
            lazy=False,
            join=JoinOption.to_one,
        ),
        create_relationship(
            target_entity_class_name='Review',
            source_identifier_column_name='book_uuid',
            source_foreign_key_column_name=None,
            target_identifier_column_name='review_uuid',
            property_name='reviews',
            nullable=False,
            lazy=True,
            join=JoinOption.to_many,
        ),
        create_relationship(
            target_entity_class_name='Genre',
            source_identifier_column_name='book_uuid',
            source_foreign_key_column_name=None,
            target_identifier_column_name='genre_uuid',
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
        'author_id', TypeOption.UUID,
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
            source_foreign_key_column_name=None,
            source_identifier_column_name='author_uuid',
            target_identifier_column_name='book_id',
            nullable=False,
            lazy=False,
            join=JoinOption.to_many,
            property_name='books',
        ),
        create_relationship(
            target_entity_class_name='Book',
            source_foreign_key_column_name=None,
            source_identifier_column_name='author_uuid',
            target_identifier_column_name='book_id',
            nullable=False,
            lazy=False,
            join=JoinOption.to_one,
            property_name='favourite_book',
        ),
    ],
    api_paths=[
        create_api_path(
            joined_entities=['book', 'review'],
            route='books/reviews',
        ),
        create_api_path(
            joined_entities=['book'],
            route='books',
        ),
    ],
)

review_entity = create_entity(
    class_name='Review',
    identifier_column=create_identifier_column(
        name='review_id', type_option=TypeOption.UUID,
    ),
    columns=[
        create_column(
            name='text', type_option=TypeOption.string,
            index=True, nullable=False,
        ),
        create_column(
            name='book_id', type_option=TypeOption.int,
            foreign_key_relationship=ForeignKeyRelationship(
                target_entity='book',
                target_entity_identifier_column_type=TypeOption.UUID,
            ),
        )
    ],
    relationships=[
        create_relationship(
            target_entity_class_name='Book',
            source_foreign_key_column_name='book_id',
            source_identifier_column_name='review_uuid',
            target_identifier_column_name='book_id',
            nullable=False,
            lazy=False,
            join=JoinOption.to_one,
        )
    ],
    operations=all_operations,
)

genre_entity = create_entity(
    class_name='Genre',
    identifier_column=create_identifier_column('genre_id', TypeOption.UUID),
    columns=[
        create_column(
            name='title',
            type_option=TypeOption.string,
        ),
    ],
    relationships=[
        create_relationship(
            target_entity_class_name='Book', nullable=True, lazy=False, join=JoinOption.to_many,
            join_table='book_genre', source_foreign_key_column_name='',
            target_identifier_column_name='book_id', source_identifier_column_name='genre_uuid'
        ),
    ],
)

book_genre_entity = create_entity(
    class_name='BookGenre',
    identifier_column=create_identifier_column('book_genre_id', TypeOption.UUID),
    columns=[
        create_column(
            'book_id',  type_option=TypeOption.int,
            foreign_key_relationship=ForeignKeyRelationship(
                target_entity='book',
                target_entity_identifier_column_type=TypeOption.UUID,
            ),
        ),
        create_column(
            'genre_id', type_option=TypeOption.int,
            foreign_key_relationship=ForeignKeyRelationship(
                target_entity='genre',
                target_entity_identifier_column_type=TypeOption.UUID,
            ),
        ),
    ],
    relationships=[
        create_relationship(
            'Book', source_foreign_key_column_name='book_id', target_identifier_column_name='book_id', nullable=False,
            lazy=False, join=JoinOption.to_one, source_identifier_column_name='book_genre_uuid',
        ),
        create_relationship(
            'Genre', source_foreign_key_column_name='genre_id', target_identifier_column_name='genre_id',
            nullable=False, lazy=False, join=JoinOption.to_one, source_identifier_column_name='book_genre_uuid',
        ),
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
