from expects import expect, be, equal
from mamba import describe, it

from genyrator.entities.Column import ForeignKey
from genyrator.entities.entity.create_entity_from_type_dict import create_entity_from_type_dict

with describe('create from type dict'):
    with it('converts identifier column'):
        result = create_entity_from_type_dict(
            class_name='Book',
            identifier_column_name='book_identifier',
            type_dict={
                'bookIdentifier': 'str',
            }
        )

        expect(result.identifier_column.python_name).to(equal('book_identifier'))

    with it('converts type? to a nullable column'):
        result = create_entity_from_type_dict(
            class_name='Book',
            identifier_column_name='book_identifier',
            type_dict={
                'bookIdentifier': 'str',
                'rating':         'float?',
                'name':           'str',
            }
        )

        expect(result.columns[1].nullable).to(be(True))
        expect(result.columns[1].python_type.value).to(be('float'))
        expect(result.columns[2].nullable).to(be(False))
        expect(result.columns[2].python_type.value).to(be('str'))

    with it('figures out foreign key columns'):
        result = create_entity_from_type_dict(
            class_name='Book',
            identifier_column_name='book_identifier',
            type_dict={
                'bookIdentifier':    'str',
                'author_identifier': 'str',
            },
            foreign_keys={(
                'author_identifier',
                'author_external_identifier',
                'str',
            )}
        )

        expect(isinstance(result.columns[1], ForeignKey)).to(be(True))
