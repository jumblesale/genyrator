from typing import List
from genyrator import Entity
import genyrator.entities.Template as Template
from genyrator.entities.Template import create_template


def create_template_config(
        module_name:    str,
        db_import_path: str,
        entities:       List[Entity],
) -> List[Template.Template]:
    return [
        create_template(Template.RootInit, '__init__', module_name=module_name),
        create_template(Template.Template, 'config'),
        create_template(
            Template.RootSchema, 'schema', db_import_path=db_import_path, entities=entities
        ),
        *[create_template(
            Template.SQLAlchemyModel, 'sqlalchemy/sqlalchemy_model',
            db_import_path=db_import_path, entity=e, out_path=Template.OutPath(('sqlalchemy/', e.class_name))
        ) for e in entities]
    ]
