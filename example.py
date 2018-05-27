import json

import dateutil.parser
from flask import Flask
from sqlalchemy.orm import joinedload

from genyrator import *
from genyrator.create_api import entity_to_api_get_endpoint_string
from genyrator.genyrator import create_column, TypeOption
from doggos.sqlalchemy import db


example_from_exemplar = """
{
    "name": "Charles",
    "age": 4,
    "goodness": 11.6,
    "dob": "2013-10-17T00:00"
}
"""

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


treat_entity = create_entity_from_exemplar(
    class_name='Treat',
    exemplar={
        "name": "snicky snax",
    },
    foreign_keys=[],
    indexes=['name'],
    relationships=[
        create_relationship('Dog', True, True, JoinOption.to_many, 'favourite_treats', 'dogs')
    ],
)
owner_dogs_entity = create_entity(
    'OwnerDogs',
    columns=[
        create_column('owner_id', TypeOption.string, 'owner.id'),
        create_column('dog_id', TypeOption.string, 'dog.id'),
    ],
    relationships=[
        create_relationship('Dog', True, False, JoinOption.to_one, None, None, 'dog'),
        create_relationship('Owner', True, False, JoinOption.to_one, None, None, 'owner'),
    ],
    table_name='owner_dogs',
)
fave_treats_entity = create_entity(
    'FavouriteTreats',
    columns=[
        create_column('dog_id', TypeOption.string, 'dog.id'),
        create_column('treat_id', TypeOption.string, 'treat.id'),
    ],
    relationships=[
        create_relationship('Dog', True, False, JoinOption.to_one,),
        create_relationship('Treat', True, False, JoinOption.to_one,),
    ],
    table_name='favourite_treats',
)
dog_entity = create_entity_from_exemplar(
    class_name='Dog',
    exemplar=json.loads(example_from_exemplar),
    foreign_keys=[('ownerId', 'owner')],
    indexes=['name'],
    relationships=[
        create_relationship('Owner', False, False, JoinOption.to_many, 'owner_dogs', 'owners'),
        create_relationship('OwnerDogs', False, False, JoinOption.to_many, None, 'owner_dogs'),
        create_relationship('Treat', True, False, JoinOption.to_one, 'favourite_treats', 'favourite_treat'),
    ]
)
owner_entity = create_entity(
    'Owner',
    [create_column('owner_id', TypeOption.string)],
    [create_relationship('Dog', False, True, JoinOption.to_many, 'owner_dogs', 'dogs')]
)

# print(dog_entity)
# print(owner_entity)
# print(entity_to_api_get_endpoint_string(dog_entity, 'dogs'))
# print(dog_entity.to_create_json_string())
args = {"out_dir_db_models": 'db',
        "out_dir_types":     'types',
        "db_import":         'from doggos.sqlalchemy import db',
        "parent_module":     'doggos',
        "entities":          [fave_treats_entity, owner_dogs_entity, dog_entity, owner_entity, treat_entity],
        }

create_entity_files(**args)
print(dog_entity.to_sqlalchemy_type_constructor())
print(dog_entity.to_type_constructor_string())

from doggos.db import Dog, Owner


@app.route('/')
def get():
    data = json.loads(example_from_exemplar)
    data['dob'] = dateutil.parser.parse(data['dob'])
    charles = Dog(**data)
    owner = Owner(owner_id='1', dogs=[charles])
    db.session.add(owner)
    db.session.commit()
    dogs = Dog.query.options(joinedload('owner_dogs').joinedload('owner')).all()
    owners = Owner.query.all()
    owner = owners[0]
    print(owner.to_owner())
    print(dogs)
    return 'hello'


if __name__ == '__main__':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
    db.init_app(app)
    with app.app_context():
        db.drop_all()
        db.create_all()
    app.run(debug=True)
