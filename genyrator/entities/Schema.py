from typing import List
import attr

from genyrator.entities.Entity import Entity
from genyrator.entities.File import File
from genyrator.entities.Template import Template


@attr.s
class Schema(object):
    module_name: str =            attr.ib()
    entities:    List[Entity] =   attr.ib()
    templates:   List[Template] = attr.ib()
    files:       List[File] =     attr.ib()
