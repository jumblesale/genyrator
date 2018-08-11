import dateutil

from genyrator.entities.Column import create_column, create_identifier_column
from genyrator.entities.Entity import create_entity, create_entity_from_type_dict, APIPaths, create_api_path, create_additional_property
from genyrator.entities.Relationship import create_relationship, JoinOption
from genyrator.entities.Schema import create_schema
from genyrator.types import TypeOption

from doggos import app, db
from doggos.sqlalchemy.model import Dog, Owner, OwnerDogs

treat_entity = create_entity(
    class_name='Treat',
    columns=[],
    identifier_column=create_column('name', TypeOption.string),
    relationships=[
        create_relationship('Dog', True, True, JoinOption.to_many, 'favourite_treats', 'dogs')
    ],
)
owner_dogs_entity = create_entity(
    'OwnerDogs',
    columns=[
        create_column('owner_id', TypeOption.string, 'owner.id'),
        create_column('dog_id', TypeOption.string, 'dog.id'),
        create_column('current_owner', TypeOption.bool),
    ],
    identifier_column=create_identifier_column('ownerDogId', TypeOption.int),
    relationships=[
        create_relationship('Dog', True, False, JoinOption.to_one, None, None,),
        create_relationship('Owner', True, False, JoinOption.to_one, None, None,),
    ],
    table_name='owner_dogs',
    additional_properties=[create_additional_property(property_name='__versioned__', property_value='{}')]
)
fave_treats_entity = create_entity(
    'FavouriteTreats',
    columns=[
        create_column('dog_id', TypeOption.string, 'dog.id'),
        create_column('treat_id', TypeOption.string, 'treat.id'),
    ],
    identifier_column=create_identifier_column('treatId', TypeOption.int),
    relationships=[
        create_relationship('Dog', True, False, JoinOption.to_one,),
        create_relationship('Treat', True, False, JoinOption.to_one,),
    ],
    table_name='favourite_treats',
)

example_from_dict = {
    "dogId": "int",
    "name": "str",
    "age": "int",
    "goodness": "float",
    "dob": "datetime",
    "pug": "bool"
}

dog_entity = create_entity_from_type_dict(
    class_name='Dog',
    type_dict=example_from_dict,
    identifier_column_name='dogId',
    foreign_keys={('ownerId', 'owner')},
    indexes={'name'},
    relationships=[
        create_relationship('Owner', False, False, JoinOption.to_many, 'owner_dogs', 'owners'),
        create_relationship('OwnerDogs', False, False, JoinOption.to_many, None, 'owner_dogs'),
        create_relationship('Treat', True, False, JoinOption.to_one, 'favourite_treats', 'favourite_treat'),
    ],
    uniques=[['name', 'goodness'], ['name', 'age']],
    api_paths=APIPaths([
        create_api_path(['owner_dogs', 'owner'], 'owner_dogs/owners', 'dog-owners')
    ]),
)
owner_entity = create_entity(
    'Owner',
    create_identifier_column('owner_id', TypeOption.string),
    [],
    [create_relationship('Dog', False, True, JoinOption.to_many, 'owner_dogs', 'dogs')]
)
entities = [dog_entity, owner_entity, fave_treats_entity, owner_dogs_entity, treat_entity]

schema = create_schema(
    module_name='doggos',
    entities=entities,
)
schema.write_files()

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        charles = Dog(
            dog_id=1,
            name='Charles',
            age=4,
            goodness=11.3,
            dob=dateutil.parser.parse("2013-10-17T00:00"),
            pug=True,
        )
        owner = Owner(
            owner_id=1,
        )
        owner_dogs = OwnerDogs(
            owner_id=1,
            dog_id=1,
            current_owner=True,
            dog=charles,
            owner=owner
        )
        db.session.add(owner_dogs)
        db.session.commit()

    app.run(debug=True)
