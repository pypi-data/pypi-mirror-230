from sqlalchemy.dialects.postgresql import ARRAY

from ul_db_utils.model.base_model import BaseModel
from ul_db_utils.modules.db import db


class ApiUser(BaseModel):
    __tablename__ = 'api_user'
    __table_args__ = {"comment": "Пользователь API"}

    date_expiration = db.Column(db.DateTime(), nullable=False, comment="Срок действия доступа")
    name = db.Column(db.String(255), unique=True, nullable=False, comment="Имя пользователя")
    note = db.Column(db.Text(), nullable=False, comment="Примечание")
    permissions = db.Column(ARRAY(db.Integer()), nullable=False, comment="Список разрешений")
