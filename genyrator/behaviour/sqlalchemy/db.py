from functools import lru_cache

from flask_sqlalchemy import SQLAlchemy


class DBNotInitialisedException(Exception):
    message = "It looks like you're trying to use genyrator without having "
    "initialised the db object first! Call `init_genyrator` with your SQLAlchemy "
    "db instance before trying to use any of the generated code."


def init_genyrator(
    sqlalchemy_instance: SQLAlchemy,
):
    get_db_instance._db_instance = sqlalchemy_instance


def get_db_instance():
    if not hasattr(get_db_instance, '_db_instance'):
        raise DBNotInitialisedException(DBNotInitialisedException.message)
    else:
        return get_db_instance._db_instance
