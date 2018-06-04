from typing import List, Optional, NewType, Tuple, NamedTuple
import attr
from jinja2 import Template as JinjaTemplate

from genyrator.entities.Entity import Entity


OutPath = NewType('OutPath', Tuple[str, str])
Import = NamedTuple('Import',
    [('module_name', str),
     ('imports',     List[str])])


@attr.s
class Template(object):
    template_file_name: str =               attr.ib()
    template_file_path: str =               attr.ib()
    out_path:           Optional[OutPath] = attr.ib()

    def create_template(self):
        with open(self.template_file_path) as f:
            template = JinjaTemplate(f.read())
        return template

    def render(self):
        return self.create_template().render(template=self)


def create_template(
        constructor,
        template_file_name: str,
        out_path: Optional[OutPath]=None,
        **kwargs,
) -> Template:
    return constructor(
        template_file_name=template_file_name,
        template_file_path='templates/{}.j2'.format(template_file_name),
        out_path=out_path,
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
class SQLAlchemyModel(Template):
    db_import_path: str = attr.ib()
    entity: Entity =      attr.ib()


@attr.s
class SQLAlchemyInit(Template):
    db_import_path: str =          attr.ib()
    imports:        List[Import] = attr.ib()


@attr.s
class RestplusModel(Template):
    entity: Entity = attr.ib()


@attr.s
class Resource(Template):
    entity:            Entity = attr.ib()
    restplus_template: str =    attr.ib()
