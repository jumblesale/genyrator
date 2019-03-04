from expects import expect, equal
from mamba import description, it

from genyrator import create_schema
from genyrator.entities.Schema import DBImport

with description('create_schema'):
    with it('converts a DBImport to a import string'):
        schema = create_schema(
            module_name='module_name',
            entities=[],
            db_import=DBImport('db_module', 'db_variable'),
        )

        expect(schema.templates.root_files[0].db_import_statement)\
            .to(equal('from db_module import db_variable as db'))
