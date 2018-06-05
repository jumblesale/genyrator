from typing import List, Optional
import attr

from genyrator.entities.Entity import Entity
from genyrator.entities.File import create_files_from_template_config, FileList
from genyrator.entities.Template import Template
from genyrator.template_config import create_template_config


@attr.s
class Schema(object):
    module_name: str =            attr.ib()
    entities:    List[Entity] =   attr.ib()
    templates:   List[Template] = attr.ib()
    files:       FileList =       attr.ib()

    def write_files(self) -> None:
        for file_list in self.files:
            [f.write() for f in file_list]

    def write_resources(self):
        for resource in self.files.resources:
            resource.write()

    def write_db_models(self):
        for model in self.files.db_models:
            model.write()

    def write_core_files(self):
        for core_file in self.files.core:
            core_file.write()


def create_schema(
        module_name:    str,
        entities:       List[Entity],
        db_import_path: Optional[str]=None,
        file_path:      Optional[List[str]]=None,
) -> Schema:
    db_import_path = db_import_path if db_import_path else '{}.sqlalchemy'.format(module_name)
    file_path = file_path if file_path else [module_name]
    template_config = create_template_config(
        module_name,
        db_import_path,
        entities,
    )
    file_list = create_files_from_template_config(file_path, template_config)
    return Schema(
        module_name=module_name,
        entities=entities,
        templates=template_config,
        files=file_list,
    )
