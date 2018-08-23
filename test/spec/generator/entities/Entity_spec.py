from mamba import description, it
from expects import expect, equal

from genyrator.entities.Entity import create_entity
from genyrator.entities.Column import create_column, create_identifier_column
from genyrator.types import TypeOption


with description('create_entity'):
    with it('adds unique on identifier if it does not exist'):
        entity = create_entity(
            'Test',
            create_identifier_column('test_id', TypeOption.string),
            [
                create_column('id', TypeOption.int, index=True, nullable=False),
                create_column('name', TypeOption.string, index=False, nullable=True),
            ],
            uniques=[],
        )

        expect(entity.uniques).to(equal([['test_id']]))

    with it('does not add unique on identifier if it does exist'):
        entity = create_entity(
            'Test',
            create_identifier_column('test_id', TypeOption.string),
            [
                create_column('id', TypeOption.int, index=True, nullable=False),
                create_column('name', TypeOption.string, index=False, nullable=True),
            ],
            uniques=[['test_id']],
        )

        expect(entity.uniques).to(equal([['test_id']]))
