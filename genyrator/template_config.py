from typing import List, NamedTuple
from genyrator import Entity
import genyrator.entities.Template as Template
from genyrator.entities.Template import create_template

TemplateConfig = NamedTuple('TemplateConfig', [
    ('root_files', List[Template.Template]),
    ('core',       List[Template.Template]),
    ('db_init'  ,  List[Template.Template]),
    ('db_models',  List[Template.Template]),
    ('resources',  List[Template.Template]), ])


def create_template_config(
        module_name:     str,
        db_import_path:  str,
        entities:        List[Entity],
        api_name:        str,
        api_description: str,
) -> TemplateConfig:
    root_files = [
        create_template(
            Template.RootInit, ['__init__'], module_name=module_name, db_import_path=db_import_path,
        ),
        create_template(Template.Config, ['config'], module_name=module_name),
    ]
    core_files = [
        create_template(Template.Template, ['core', 'convert_case']),
        create_template(Template.ConvertDict, ['core', 'convert_dict'], module_name=module_name),
    ]
    db_init = [
        create_template(Template.Template, ['sqlalchemy', '__init__']),
    ]
    db_models = [
        *[create_template(
            Template.SQLAlchemyModel, ['sqlalchemy', 'model', 'sqlalchemy_model'],
            db_import_path=db_import_path, entity=e, out_path=Template.OutPath((['sqlalchemy', 'model'], e.class_name))
        ) for e in entities],
        create_template(
            Template.SQLAlchemyModelInit, ['sqlalchemy', 'model', '__init__'], db_import_path=db_import_path,
            imports=[Template.Import(e.class_name, [e.class_name]) for e in entities], module_name=module_name,
        ),
        create_template(Template.ModelToDict, ['sqlalchemy', 'model_to_dict'], module_name=module_name),
    ]
    resources = [
        create_template(
            Template.RootSchema, ['schema'], module_name=module_name, entities=entities
        ),
        *[create_template(
            Template.Resource, ['resources', 'resource'],
            entity=e, out_path=Template.OutPath((['resources'], e.class_name)),
            db_import_path=db_import_path, module_name=module_name,
            restplus_template=create_template(
                Template.RestplusModel, ['resources', 'restplus_model'], entity=e
            ).render()
        ) for e in entities],
        create_template(
            Template.ResourcesInit, ['resources', '__init__'], entities=entities,
            module_name=module_name, api_name=api_name, api_description=api_description,
        ),
    ]
    return TemplateConfig(
        root_files=root_files,
        core=core_files,
        db_init=db_init,
        db_models=db_models,
        resources=resources,
    )
