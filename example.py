import json
import datetime
import dateutil.parser
from flask import Flask
from flask_restplus import Api
from sqlalchemy.orm import joinedload, class_mapper

from genyrator import *
from genyrator.create_api import entity_to_api_get_endpoint_string, render_api_endpoints, create_api_files, APIPath
from genyrator.genyrator import create_column, TypeOption


example_from_exemplar = """
{
    "dogId": 1,
    "name": "Charles",
    "age": 4,
    "goodness": 11.6,
    "dob": "2013-10-17T00:00",
    "pug": true
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
        create_column('current_owner', TypeOption.bool),
    ],
    relationships=[
        create_relationship('Dog', True, False, JoinOption.to_one, None, None,),
        create_relationship('Owner', True, False, JoinOption.to_one, None, None,),
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
    ],
    uniques=[['name', 'goodness'], ['name', 'age']]
)
owner_entity = create_entity(
    'Owner',
    [create_column('owner_id', TypeOption.string)],
    [create_relationship('Dog', False, True, JoinOption.to_many, 'owner_dogs', 'dogs')]
)

args = {"out_dir_db_models": 'db',
        "out_dir_types":     'types',
        "db_import":         'from doggos.sqlalchemy import db',
        "parent_module":     'doggos',
        "entities":          [fave_treats_entity, owner_dogs_entity, dog_entity, owner_entity, treat_entity],
        }

create_entity_files(**args)
create_api_files(
    'doggos/restplus',
    'dogs',
    'from doggos import model_to_dict',
    'from doggos.sqlalchemy import db\nfrom doggos.db import *',
    [dog_entity, owner_entity, ],
    [APIPath(dog_entity, ['owner_dogs', 'owner'], 'dog/<id>/owner_dogs/owners')],
)

import doggos.db as doggo_db
from doggos.sqlalchemy import db
import dateutil.parser

if __name__ == '__main__':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
    db.init_app(app)
    with app.app_context():
        db.drop_all()
        db.create_all()
        charles = doggo_db.Dog(
            dog_id=1,
            name='Charles',
            age=4,
            goodness=11.3,
            dob=dateutil.parser.parse("2013-10-17T00:00"),
            pug=True,
        )
        owner = doggo_db.Owner(
            owner_id=1,
        )
        owner_dogs = doggo_db.OwnerDogs(
            owner_id=1,
            dog_id=1,
            current_owner=True,
            dog=charles,
            owner=owner
        )
        db.session.add(owner_dogs)
        db.session.commit()

    from doggos.restplus import endpoints

    api = Api(app)
    api.add_namespace(endpoints.dogs)

    app.run(debug=True)
