from typing import Optional

from genyrator import TypeOption


class Property(object):
    def __init__(
            self,
            type:       TypeOption,
            nullable:   Optional[bool]=None,
            identifier: Optional[bool]=None,
    ):
        self.type =       type
        self.nullable =   nullable if nullable is not None else False
        self.identifier = identifier if identifier is not None else False
