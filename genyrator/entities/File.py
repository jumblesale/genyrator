import os
from typing import List, NamedTuple
import attr

from genyrator.entities import Template
from genyrator.template_config import TemplateConfig

FileList = NamedTuple('FileList', [
    ('root_files',       List['File']),
    ('core',             List['File']),
    ('db_models',        List['File']),
    ('fixtures',         List['File']),
    ('db_init',          List['File']),
    ('domain_models',    List['File']),
    ('resources',        List['File']), ])


@attr.s
class File(object):
    file_name: str =       attr.ib()
    file_path: List[str] = attr.ib()
    contents:  str =       attr.ib()

    def write(self):
        file_path = os.path.join(*self.file_path)
        try:
            os.makedirs(file_path)
        except FileExistsError:
            ...
        file = os.path.join(file_path, self.file_name)
        with open(file, 'w') as f:
            f.write(self.contents)


def create_files_from_template_config(
        file_path:       List[str],
        template_config: TemplateConfig
) -> FileList:
    args = {}
    for key, templates in template_config._asdict().items():
        args[key] = [create_file_from_template(file_path, template) for template in templates]
    return FileList(**args)


def create_file_from_template(file_path: List[str], template: Template) -> File:
    if template.out_path:
        file_path = file_path + template.out_path[0]
        file_name = '{}.py'.format(template.out_path[1])
    else:
        file_path = file_path + template.relative_path
        file_name = '{}.py'.format(template.template_name)
    return File(
        file_name=file_name,
        file_path=file_path,
        contents=template.render(),
    )
