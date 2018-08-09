from typing import List

from genyrator import create_entity, create_column, TypeOption, create_identifier_column, create_relationship, \
    JoinOption
from genyrator.entities.Entity import OperationOption, all_operations, Entity
from genyrator.entities.Schema import create_schema, Schema

book_entity = create_entity(
    class_name='Book',
    identifier_column=create_identifier_column(
        name='book_id', type_option=TypeOption.string,
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
    ],
    relationships=[
        create_relationship(
            target_entity_class_name='Author',
            nullable=False,
            lazy=False,
            join=JoinOption.to_one,
        )
    ],
    operations=all_operations
)

author_entity = create_entity(
    class_name='Author',
    identifier_column=create_identifier_column(
        'author_id', TypeOption.string,
    ),
    columns=[
        create_column(
            name='name', type_option=TypeOption.string,
            index=True, nullable=False,
        ),
    ]
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
        book_entity, author_entity
    ])
    write_app(schema)
