from typing import Any, Mapping

import attr


@attr.s
class Relationship:
    target: Any =                   attr.ib()
    target_identifier_column: str = attr.ib()
    lazy:   bool =                  attr.ib()


@attr.s
class DomainModel:
    relationship_map:       Mapping[str, Relationship] = attr.ib()
    identifier_column_name: str =                        attr.ib()