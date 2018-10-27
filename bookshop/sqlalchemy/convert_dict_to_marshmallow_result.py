from typing import Optional, Union, List, Mapping, Any

from flask_marshmallow.sqla import ModelSchema
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import noload

from bookshop.sqlalchemy import db
from bookshop.core.convert_dict import json_dict_to_python_dict
from bookshop.domain.types import DomainModel
from bookshop.sqlalchemy.convert_properties import convert_properties_to_sqlalchemy_properties
from bookshop.sqlalchemy.join_entities import create_joined_entity_map


def convert_dict_to_marshmallow_result(
        data:              Mapping[str, Any],
        identifier:        str,
        identifier_column: str,
        domain_model:      DomainModel,
        sqlalchemy_model:  DeclarativeMeta,
        schema:            ModelSchema,
        patch_data:        Optional[Mapping[str, Any]] = None,
) -> Union[ModelSchema, List[str]]:
    result = sqlalchemy_model.query.filter_by(
        **{identifier_column: identifier}
    ).options(noload('*')).first()

    if patch_data is not None:
        data = {**data, **patch_data}

    joined_entities_or_errors = create_joined_entity_map(
        domain_model,
        data,
    )

    if isinstance(joined_entities_or_errors, list):
        return joined_entities_or_errors

    data = convert_properties_to_sqlalchemy_properties(
        domain_model,
        joined_entities_or_errors,
        json_dict_to_python_dict(data),
    )

    if result is not None:
        # don't use the 'id' from the json request
        data = {**data, **{'id': result.id}}

    marshmallow_result = schema.load(
        json_dict_to_python_dict(data),
        session=db.session,
        instance=result,
    )

    return marshmallow_result
