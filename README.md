# Genyrator

A tool for generating a [Flask](http://flask.pocoo.org/) web app from an abstract
definition. The app is based on [Flask-RESTPlus](https://flask-restplus.readthedocs.io/en/stable/),
[Flask-Marshmallow](https://flask-marshmallow.readthedocs.io/en/latest/) and
[Flask-SQLAlchemy](http://flask-sqlalchemy.pocoo.org/2.3/).

## Generate an app

An app is generated from entities that are related together. Below is a minimal
example of people and houses. For a more detailed example see [`bookshop.py`](./bookshop.py).

```python

house_entity = create_entity(
  class_name='House',
  identifier_column=create_identifier_column(
    name='house_id', type_option=TypeOption.UUID,
  ),
  columns=[
    create_column(
      name='name', type_option=TypeOption.string,
      index=True, nullable=False,
    ),
    create_column(
      name='created_at', type_option=TypeOption.datetime,
      nullable=False,
    ),
  ],
  relationships=[
    create_relationship(
      target_entity_class_name='Person',
      source_foreign_key_column_name=None,
      source_identifier_column_name='person_id',
      target_identifier_column_name='house_id',
      join=JoinOption.to_many,
      property_name='houses',
    ),
  ]
)

person_entity = create_entity(
  class_name='Person',
  identifier_column=create_identifier_column(
    name='person_id', type_option=TypeOption.UUID,
  ),
  columns=[
    create_column(
      name='name', type_option=TypeOption.string,
      index=True, nullable=False,
    ),
    create_column(
      name='book_id', type_option=TypeOption.int, # int because the SQLAlchemy primary keys are int
      foreign_key_relationship=ForeignKeyRelationship(
        target_entity='person',
        target_entity_identifier_column_type=TypeOption.UUID,
      ),
    ),
  ],
  relationships=[
    create_relationship(
      target_entity_class_name='House',
      source_foreign_key_column_name='house_id',
      source_identifier_column_name='person_id',
      target_identifier_column_name='house_id',
      nullable=False,
      lazy=False,
      join=JoinOption.to_one,
    ),
  ]
)

# Create a schema for the app that will be written into a module called 'houses'
schema = create_schema(
  module_name='houses',
  entities=[house_entity, person_entity],
)

# Write out all files for the app
schema.write_files()
```

## Deploying

Bump the version in `setup.py` then run `make deploy`.