from functools import lru_cache

from flask_sqlalchemy import SQLAlchemy


def init_genyrator(
    sqlalchemy_instance: SQLAlchemy,
):
    get_db_instance._db_instance = sqlalchemy_instance


@lru_cache()
def get_db_instance():
    if get_db_instance._db_instance is None:
        ...
    else:
        return get_db_instance._db_instance
