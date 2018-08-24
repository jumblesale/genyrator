from typing import List, Optional, NewType, Tuple, NamedTuple
import attr
from jinja2 import Template as JinjaTemplate, StrictUndefined

from genyrator.entities.Entity import Entity
from genyrator.path import create_relative_path

OutPath = NewType('OutPath', Tuple[List[str], str])
Import = NamedTuple('Import',
                    [('module_name', str),
                     ('imports',     List[str]), ])


@attr.s
class Template(object):
    template_name:      str =               attr.ib()
    template_file_name: str =               attr.ib()
    template_file_path: List[str] =         attr.ib()
    relative_path:      List[str] =         attr.ib()
    out_path:           Optional[OutPath] = attr.ib()

    def create_template(self):
        path = create_relative_path(
            [*self.template_file_path, self.template_file_name]
        )
        with open(path) as f:
            template = JinjaTemplate(f.read(), undefined=StrictUndefined)
        return template

    def render(self):
        return self.create_template().render(template=self)


def create_template(
        constructor,
        template_path: Optional[List[str]] = None,
        out_path:      Optional[OutPath] = None,
        **kwargs,
) -> Template:
    relative_path = template_path[0:-1]
    path = ['genyrator', 'templates'] + relative_path
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
    db_import_path: str = attr.ib()
    module_name:    str = attr.ib()


@attr.s
class RootSchema(Template):
    module_name: str =          attr.ib()
    entities:    List[Entity] = attr.ib()


@attr.s
class ConvertDict(Template):
    module_name: str = attr.ib()


@attr.s
class SQLAlchemyModel(Template):
    db_import_path: str = attr.ib()
    entity: Entity =      attr.ib()


@attr.s
class ModelToDict(Template):
    module_name: str = attr.ib()


@attr.s
class Config(Template):
    module_name: str = attr.ib()


@attr.s
class SQLAlchemyModelInit(Template):
    module_name:    str =          attr.ib()
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


@attr.s
class DomainModel(Template):
    entity:      Entity = attr.ib()
    module_name: str =    attr.ib()


@attr.s
class ConvertProperties(Template):
    module_name: str = attr.ib()


@attr.s
class JoinEntities(Template):
    module_name: str = attr.ib()
