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
    dog_entity = create_entity_from_exemplar(
        class_name='Dog',
        exemplar=json.loads(example_from_exemplar),
        foreign_keys=[('ownerId', 'owner')],
        indexes=['name'],
        relationships=[create_relationship('Owner', True, False, JoinOption.to_one, 'owner_dogs')]
    )
    print(dog_entity)
    create_entity_files(
        out_dir_db_models='db',
        out_dir_types='types',
        db_import='from genyrator import db',
        parent_module='doggos',
        entities=[dog_entity],
    )
