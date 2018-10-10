import importlib

from sqlalchemy.ext.declarative import DeclarativeMeta
from flask_restplus import Model

from bookshop.core import convert_case
from bookshop.domain.types import DomainModel


def convert_sqlalchemy_model_to_domain_model(
        sqlalchemy_model: DeclarativeMeta
) -> DomainModel:
    class_name = sqlalchemy_model.__class__.__name__
    domain_module = importlib.import_module(f'bookshop.domain.{class_name}')
    return getattr(domain_module, convert_case.to_python_name(class_name))


def convert_sqlalchemy_class_to_domain_model(
        sqlalchemy_class: Model,
):
    class_name = sqlalchemy_class.__name__
    domain_module = importlib.import_module(f'data_pipeline.generated.domain.{class_name}')
    return getattr(domain_module, convert_case.to_python_name(class_name))
