import os
from pathlib import Path
from typing import List


def get_root_path_list() -> List[str]:
    path = Path(os.path.dirname(os.path.realpath(__file__)))
    return list(path.parent.parts)


def create_relative_path(paths: List[str]) -> str:
    return os.path.join(
            *get_root_path_list(),
            *paths,
        )
