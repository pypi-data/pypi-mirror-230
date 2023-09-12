from typing import Union, Optional, Type
from uuid import UUID

from sqlalchemy.exc import NoResultFound as NoResultFoundError

from ul_db_utils.model.base_api_user_log_model import BaseApiUserLogModel
from ul_db_utils.model.base_model import BaseModel
from ul_db_utils.model.base_user_log_model import BaseUserLogModel
from ul_db_utils.modules.custom_query import CustomQuery


def query_soft_delete(
    model: Union[Type[BaseModel], Type[BaseUserLogModel], Type[BaseApiUserLogModel]],
    instance_id: UUID,
    user_modified_id: Optional[UUID] = None,
    query: Optional[CustomQuery] = None,
) -> Union[BaseModel, BaseUserLogModel, BaseApiUserLogModel]:
    if not issubclass(model, (BaseModel, BaseUserLogModel, BaseApiUserLogModel)):
        raise ValueError(f'model must be inherited of {BaseModel} / {BaseUserLogModel} / {BaseApiUserLogModel}')
    if issubclass(model, (BaseModel, BaseUserLogModel, BaseApiUserLogModel)):
        assert user_modified_id is not None, "user_modified_id must be given"
    if query is not None:
        if not isinstance(query, CustomQuery):
            raise ValueError(f"query must be type of {CustomQuery}, got {type(query)}")
        instance = query\
            .with_deleted()\
            .filter(model.id == instance_id)\
            .first()
        if instance is None:
            raise NoResultFoundError(f'{model.__name__} not found')
        if instance.is_alive:
            if issubclass(model, (BaseUserLogModel, BaseApiUserLogModel)):
                instance.mark_as_deleted(user_modified_id)
            elif issubclass(model, BaseModel):
                instance.mark_as_deleted()
    else:
        instance = model.query\
            .with_deleted()\
            .filter(model.id == instance_id)\
            .first()
        if instance is None:
            raise NoResultFoundError(f'{model.__name__} not found')
        if instance.is_alive:
            if issubclass(model, (BaseUserLogModel, BaseApiUserLogModel)):
                instance.mark_as_deleted(user_modified_id)
            elif issubclass(model, BaseModel):
                instance.mark_as_deleted()
    return instance
