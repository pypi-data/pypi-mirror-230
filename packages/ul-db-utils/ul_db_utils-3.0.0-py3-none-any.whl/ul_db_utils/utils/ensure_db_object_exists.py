from typing import Optional, Type

from sqlalchemy.exc import NoResultFound as NoResultFoundError

from ul_db_utils.modules.db import DbModel


def ensure_db_object_exists(model: Type[DbModel], instance: Optional[DbModel]) -> DbModel:
    if instance is None:
        raise NoResultFoundError(f"{model.__name__} not found")
    return instance
