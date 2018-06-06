from typing import Union

from genyrator import JoinOption
from genyrator.declarative.Model import Model


class Relationship(object):
    def __init__(
            self,
            target:      Union[Model, str],
            join_option: JoinOption,
    ):
        self.target =      target
        self.join_option = join_option
