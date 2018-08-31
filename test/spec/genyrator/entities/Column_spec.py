from expects import expect, have_property, be_a, equal
from mamba import description, it

from genyrator import create_column, TypeOption, Column
from genyrator.entities.Column import ForeignKey, ForeignKeyRelationship

with description('create_column'):
    with it('does not create a foreign key if no relationship is specified'):
        column = create_column(
            name='test', type_option=TypeOption.string, foreign_key_relationship=None,
        )

        expect(column).to(be_a(Column))
        expect(column).not_to(have_property('relationship'))

    with it('creates a foreign key relationship to the joined entity id column'):
        column = create_column(
            name='test', type_option=TypeOption.string,
            foreign_key_relationship=ForeignKeyRelationship(
                target_entity='EntityTable',
                target_entity_identifier_column_type=TypeOption.string,
            )
        )

        expect(column).to(be_a(ForeignKey))
        expect(column.relationship).to(equal('entity_table.id'))
