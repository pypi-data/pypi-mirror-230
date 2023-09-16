from datetime import datetime
from orjson import dumps
from sqlalchemy import Column, TIMESTAMP, text, DateTime, Boolean, Integer
from sqlalchemy.ext.declarative import declared_attr


class BasicModel:
    """
    model 基础类，定义了共用字段和共用方法
    """
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    __table_args__ = {'mysql_engine': 'InnoDB'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    create_time = Column(TIMESTAMP, default=datetime.now, nullable=True,
                         server_default=text('CURRENT_TIMESTAMP'))

    def set_attrs(self, attrs_dict):
        for key, value in attrs_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def to_dict(self):
        model_dict = {}
        for _ in self.__table__.columns:
            value = getattr(self, _.name)
            if value is None:
                value = 0 if isinstance(_.type, Integer) else ''
            model_dict[_.name] = value
        return model_dict


class EnhancedModel(BasicModel):
    """
    增加了 update_time 、is_deleted 字段
    """
    update_time = Column(DateTime, onupdate=datetime.now, default=datetime.now, comment='更新时间')
    is_deleted = Column(Boolean, default=False, comment='是否删除')
