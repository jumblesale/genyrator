from genyrator.genyrator import (
    render_db_model, JoinOption, create_relationship, create_entity_from_exemplar,
    render_type_model,
    render_type_constructor)
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
        foreign_keys=[('ownerId', 'owner.owner_id')],
        indexes=['name'],
        relationships=[create_relationship('Owner', True, False, JoinOption.to_one, 'owner_dogs')]
    )
    print(dog_entity)
    print(render_db_model(
        entity=dog_entity,
        db_import="from genyrator import db",
        types_module="doggos"
    ))
    print(render_db_model(entity=dog_entity, db_import="from doggos import db", types_module="doggos"))
    print(render_type_model(entity=dog_entity))
    print(render_type_constructor(entity=dog_entity))
