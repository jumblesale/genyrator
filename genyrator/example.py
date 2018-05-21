from genyrator.genyrator import render_templates, JoinOption, create_relationship

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
    "dob": "2013-10-17T00:00"
}
"""

# dog_entity = _entity_from_dict(example_entity)
dog_entity = _entity_from_exemplar('Dog', json.loads(example_from_exemplar))
dog_entity.relationships = [create_relationship('Owner', True, False, JoinOption.to_one)]
print(dog_entity)

db_rendered, to_type_rendered, type_constructor_rendered, tuple_rendered = render_templates(dog_entity)
print(db_rendered)
print(to_type_rendered)
print(type_constructor_rendered)
print(tuple_rendered)
