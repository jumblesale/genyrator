from typing import List, NamedTuple
from genyrator import Entity
import genyrator.entities.Template as Template
from genyrator.entities.Template import create_template

TemplateConfig = NamedTuple('TemplateConfig', [
    ('root_files',    List[Template.Template]),
    ('core',          List[Template.Template]),
    ('db_init',       List[Template.Template]),
    ('db_models',     List[Template.Template]),
    ('domain_models', List[Template.Template]),
    ('resources',     List[Template.Template]), ])


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
            db_import_path=db_import_path, entity=e, module_name=module_name,
            out_path=Template.OutPath((['sqlalchemy', 'model'], e.class_name))
        ) for e in entities],
        create_template(
            Template.SQLAlchemyModelInit, ['sqlalchemy', 'model', '__init__'], db_import_path=db_import_path,
            imports=[Template.Import(e.class_name, [e.class_name]) for e in entities], module_name=module_name,
        ),
        create_template(Template.ModelToDict, ['sqlalchemy', 'model_to_dict'], module_name=module_name),
        create_template(Template.ConvertProperties, ['sqlalchemy', 'convert_properties'], module_name=module_name),
        create_template(Template.ConvertModels, ['sqlalchemy', 'convert_between_models'], module_name=module_name),
        create_template(Template.JoinEntities, ['sqlalchemy', 'join_entities'], module_name=module_name),
        create_template(Template.Template, ['sqlalchemy', 'model', 'types']),
        create_template(
            Template.ConvertDictToMarshmallow,
            ['sqlalchemy', 'convert_dict_to_marshmallow_result'],
            module_name=module_name, db_import_path=db_import_path,
        ),
    ]
    domain_models = [
        create_template(Template.Template, ['domain', 'types']),
        *[create_template(
            Template.DomainModel, ['domain', 'domain_model'], module_name=module_name, entity=entity,
            out_path=Template.OutPath((['domain'], entity.class_name))
        ) for entity in entities]
    ]
    resources = [
        create_template(
            Template.RootSchema, ['schema'], module_name=module_name, entities=entities
        ),
        *[create_template(
            Template.Resource, ['resources', 'resource'],
            entity=entity, out_path=Template.OutPath((['resources'], entity.class_name)),
            db_import_path=db_import_path, module_name=module_name,
            restplus_template=create_template(
                Template.RestplusModel, ['resources', 'restplus_model'], entity=entity
            ).render()
        ) for entity in entities],
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
        domain_models=domain_models,
        resources=resources,
    )
