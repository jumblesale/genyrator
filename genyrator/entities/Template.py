import os
from typing import List, Optional, NewType, Tuple, NamedTuple
import attr
from jinja2 import Template as JinjaTemplate

from genyrator.entities.Entity import Entity


OutPath = NewType('OutPath', Tuple[List[str], str])
Import = NamedTuple('Import',
    [('module_name', str),
     ('imports',     List[str])])


@attr.s
class Template(object):
    template_name:      str =               attr.ib()
    template_file_name: str =               attr.ib()
    template_file_path: List[str] =         attr.ib()
    relative_path:      List[str] =         attr.ib()
    out_path:           Optional[OutPath] = attr.ib()

    def create_template(self):
        with open(os.path.join(*self.template_file_path, self.template_file_name)) as f:
            template = JinjaTemplate(f.read())
        return template

    def render(self):
        return self.create_template().render(template=self)


def create_template(
        constructor,
        template_path: Optional[List[str]]=None,
        out_path:      Optional[OutPath]=None,
        **kwargs,
) -> Template:
    relative_path = template_path[0:-1]
    path = ['templates'] + relative_path
    template_name = template_path[-1]
    return constructor(
        template_name=template_name,
        template_file_name='{}.j2'.format(template_name),
        template_file_path=path,
        out_path=out_path,
        relative_path=relative_path,
        **kwargs,
    )


@attr.s
class RootInit(Template):
    module_name: str = attr.ib()


@attr.s
class RootSchema(Template):
    db_import_path: str =          attr.ib()
    entities:       List[Entity] = attr.ib()


@attr.s
class ConvertDict(Template):
    module_name: str = attr.ib()


@attr.s
class SQLAlchemyModel(Template):
    db_import_path: str = attr.ib()
    entity: Entity =      attr.ib()


@attr.s
class SQLAlchemyModelInit(Template):
    db_import_path: str =          attr.ib()
    imports:        List[Import] = attr.ib()


@attr.s
class RestplusModel(Template):
    entity: Entity = attr.ib()


@attr.s
class Resource(Template):
    module_name:       str =    attr.ib()
    db_import_path:    str =    attr.ib()
    entity:            Entity = attr.ib()
    restplus_template: str =    attr.ib()


@attr.s
class ResourcesInit(Template):
    entities:        List[Entity] = attr.ib()
    module_name:     str =          attr.ib()
    api_name:        str =          attr.ib()
    api_description: str =          attr.ib()
