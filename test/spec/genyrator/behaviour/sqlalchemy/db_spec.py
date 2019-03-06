from expects import be_a, expect, be_none
from flask_sqlalchemy import SQLAlchemy
from mamba import description, it

from genyrator.behaviour.sqlalchemy.db import (
    init_genyrator, get_db_instance,
    DBNotInitialisedException)

from bookshop.sqlalchemy import db as bookshop_db


with description('using the db instance'):
    with it('throws if the db has not been initialized'):
        exception = None
        try:
            instance = get_db_instance()
        except DBNotInitialisedException as e:
            exception = e
        expect(exception).to_not(be_none)


    with it('provides access to the db instance'):
        init_genyrator(sqlalchemy_instance=bookshop_db)
        instance = get_db_instance()
        expect(instance).to(be_a(SQLAlchemy))
