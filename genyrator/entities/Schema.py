from typing import List, Optional, NamedTuple
import attr

from genyrator.entities.Entity import Entity
from genyrator.entities.File import create_files_from_template_config, FileList
from genyrator.template_config import create_template_config, TemplateConfig

DBImport = NamedTuple('DBImport',
    [('db_module',        str),
     ('db_variable_name', str), ]
)


@attr.s
class Schema(object):
    module_name:         str =            attr.ib()
    entities:            List[Entity] =   attr.ib()
    templates:           TemplateConfig = attr.ib()
    files:               FileList =       attr.ib()
    api_name:            str =            attr.ib()
    api_description:     str =            attr.ib()

    def write_files(self) -> None:
        for file_list in self.files:
            [f.write() for f in file_list]

    def write_resources(self):
        for resource in self.files.resources:
            resource.write()

    def write_db_init(self):
        for model in self.files.db_models:
            model.write()

    def write_db_models(self):
        for model in self.files.db_models:
            model.write()

    def write_fixtures(self):
        for model in self.files.fixtures:
            model.write()

    def write_core_files(self):
        for core_file in self.files.core:
            core_file.write()

    def write_domain_models(self):
        for domain_model in self.files.domain_models:
            domain_model.write()


def create_schema(
        module_name:     str,
        entities:        List[Entity],
        db_import:       Optional[DBImport] = None,
        api_name:        Optional[str] = None,
        api_description: Optional[str] = None,
        file_path:       Optional[List[str]] = None,
) -> Schema:
    """Create a Genyrator Schema.

    A Schema represents a collection of entities, as well as details on how to
    write the generated code.

    Args:
        module_name:      The name used for the generated module. Gets used in import statements
        entities:         A list of Entities to include in the Schema
        db_import:        A DBImport describing how to access the sqlalchemy database object used by
                          the app. Defaults to importing "db" from "{module_name}.sqlalchemy"
        api_name:         Used in the generation of the RESTPLUS API. Shows up in the generated Swagger
        api_description:  Used in the generated RESTPLUS API
        file_path:        The path to where to write the files to. Defaults to the module name - if
                          the module_name is "bookshop", the app will be written to "bookshop/"
    """
    db_import = db_import if db_import else DBImport(f'{module_name}.sqlalchemy', 'db')
    db_import_statement = f'from {db_import.db_module} import {db_import.db_variable_name} as db'
    file_path =  file_path if file_path else [module_name]
    api_name = api_name if api_name else module_name
    api_description = api_description if api_description else ''
    template_config = create_template_config(
        module_name=module_name,
        db_import_statement=db_import_statement,
        entities=entities,
        api_name=api_name,
        api_description=api_description,
    )
    file_list = create_files_from_template_config(file_path, template_config)
    return Schema(
        module_name=module_name,
        entities=entities,
        templates=template_config,
        files=file_list,
        api_name=api_name,
        api_description=api_description,
    )
