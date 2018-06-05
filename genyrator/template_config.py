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
        create_template(Template.RootInit, ['__init__'], module_name=module_name),
        create_template(Template.Template, ['config']),
        create_template(
            Template.RootSchema, ['schema'], db_import_path=db_import_path, entities=entities
        ),
        create_template(Template.Template,    ['core', 'convert_case']),
        create_template(Template.ConvertDict, ['core', 'convert_dict'], module_name=module_name),
        *[create_template(
            Template.SQLAlchemyModel, ['sqlalchemy', 'model', 'sqlalchemy_model'],
            db_import_path=db_import_path, entity=e, out_path=Template.OutPath((['sqlalchemy', 'model'], e.class_name))
        ) for e in entities],
        create_template(
            Template.SQLAlchemyModelInit, ['sqlalchemy', 'model', '__init__'], db_import_path=db_import_path,
            imports=[Template.Import(e.class_name, [e.class_name]) for e in entities],
        ),
        create_template(Template.Template, ['sqlalchemy', 'model_to_dict']),
        create_template(Template.Template, ['sqlalchemy', '__init__']),
        *[create_template(
            Template.Resource, ['resources', 'resource'],
            entity=e, out_path=Template.OutPath((['resources'], e.class_name)),
            db_import_path=db_import_path, module_name=module_name,
            restplus_template=create_template(
                Template.RestplusModel, ['resources', 'restplus_model'], entity=e
            ).render()
        ) for e in entities],
    ]
