from genyrator import *
import json

example_entity = {
    "class_name": 'Dog',
    "columns": [
        {"name": "name", "type": "string"}, {"name": "age", "type": "int"}
    ]
}

example_from_exemplar = """
{
    "name": "Charles",
    "age": 4,
    "goodness": 11.6,
    "dob": "2013-10-17T00:00",
    "ownerId": 1
}
"""

if __name__ == '__main__':
    treat_entity = create_entity_from_exemplar(
        class_name='Treat',
        exemplar={
            "name": "snicky snax",
        },
        foreign_keys=[],
        indexes=[],
        relationships=[
            create_relationship('Dog', True, True, JoinOption.to_many)
        ]
    )
    dog_entity = create_entity_from_exemplar(
        class_name='Dog',
        exemplar=json.loads(example_from_exemplar),
        foreign_keys=[('ownerId', 'owner')],
        indexes=['name'],
        relationships=[
            create_relationship('Owner', False, False, JoinOption.to_many, 'owner_dogs', 'owners'),
            create_relationship('Treat', True, False, JoinOption.to_one, None, 'favourite_treat'),
        ]
    )
    owner_entity = create_entity(
        'Owner',
        [create_column('owner_id', TypeOption.string)],
        [create_relationship('Dog', False, True, JoinOption.to_many, None, 'dogs')]
    )

    print(dog_entity)
    print(owner_entity)
    print(entity_to_api_get_endpoint_string(dog_entity, 'dogs'))
    create_entity_files(
        out_dir_db_models='db',
        out_dir_types='types',
        db_import='from genyrator import db',
        parent_module='doggos',
        entities=[dog_entity, owner_entity, treat_entity],
    )
