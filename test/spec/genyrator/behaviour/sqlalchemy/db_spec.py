from expects import expect, be_none
from mamba import description, it

from genyrator.behaviour.sqlalchemhy.db import get_db_instance

with description('accessing the db instance'):
    with it('loads the db instance from a module'):
        instance = get_db_instance(
            module_name='bookshop.sqlalchemy',
            variable_name='db',
        )
        expect(instance).not_to(be_none)
