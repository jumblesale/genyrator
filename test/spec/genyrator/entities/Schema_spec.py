from expects import expect, equal
from mamba import description, it

from genyrator import create_schema

with description('create_schema'):
    with it('converts a DBImport to a import string'):
        schema = create_schema(
            module_name='module_name',
            entities=[],
            db_import='from db_module import db_variable as db',
        )

        expect(schema.templates.root_files[0].db_import_statement)\
            .to(equal('from db_module import db_variable as db'))
