import math
from typing import List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from fastapi_assistant.bases.model import EnhancedModel
from fastapi_assistant.bases.schema import ListArgsSchema, ListFilterSchema, ListOrderSchema, RespListSchema, \
    ListKeySchema, ListCustomizeFilterSchema
from fastapi_assistant.db.sqlalchemy import get_or_create, update_or_create


class BasicDao(object):
    Model = EnhancedModel

    def __init__(self, operator_id=0):
        self.operator_id = operator_id

    @staticmethod
    async def create(db: Session, obj: Model, is_commit: bool = True):
        """
        创建一条记录
        :param db:
        :param obj:
        :param is_commit:
        :return:
        """
        try:
            db.add(obj)
            db.flush()
        except Exception as e:
            db.rollback()
            raise e
        if is_commit:
            db.commit()

    async def get_or_create(self, db: Session, defaults=None, is_commit: bool = True, **kwargs) -> Tuple[Model, bool]:
        """
        获取一个或创建一个 defaults
        :param db:
        :param defaults: 扩充条件
        :param is_commit: 是否提交
        :param kwargs: 查询条件
        :return:
        """
        obj, created = await get_or_create(db, self.Model, defaults, **kwargs)
        if is_commit:
            db.commit()
        return obj, created

    async def update_or_create(self, db: Session, defaults=None, is_commit=True, **kwargs) -> Tuple[Model, bool]:
        """
        更新或创建一个
        :param db:
        :param defaults: 更新内容
        :param is_commit: 是否提交
        :param kwargs: 查询条件
        :return:
        """
        obj, created = await update_or_create(db, self.Model, defaults, **kwargs)
        if is_commit:
            db.commit()
        return obj, created

    async def get(self, db: Session, pk: int) -> Model:
        """
        获取一条数据
        :param db:
        :param pk: id
        :return: 返回这个模型数据
        """
        filters = [self.Model.id == pk, ]
        if hasattr(self.Model, 'is_deleted'):
            filters.append(~self.Model.is_deleted)
        return db.query(self.Model).filter(*filters).first()

    async def update(self, db: Session, pk: int, update_data: dict, is_commit: bool = True):
        """
        更新一条数据
        :param db:
        :param pk:
        :param update_data:
        :param is_commit: 是否提交
        """
        filters = [self.Model.id == pk, ]
        if hasattr(self.Model, 'is_deleted'):
            filters.append(~self.Model.is_deleted)
        try:
            db.query(self.Model).filter(*filters).update(update_data, synchronize_session=False)
            db.flush()
        except Exception as e:
            db.rollback()
            raise e
        if is_commit:
            db.commit()

    async def delete(self, db: Session, pk: int, is_commit: bool = True):
        """
        删除一条数据，定义了 is_deleted 进行软删除，否者真删除
        :param db:
        :param pk: id
        :param is_commit: 是否提交
        """
        filters = [self.Model.id == pk, ]
        try:
            if hasattr(self.Model, 'is_deleted'):
                filters.append(~self.Model.is_deleted)
                db.query(self.Model).filter(*filters).update({self.Model.is_deleted: True}, synchronize_session=False)
            else:
                db.query(self.Model).filter(*filters).delete()
            db.commit()
        except Exception as e:
            raise e
        if is_commit:
            db.commit()

    async def count(self, db: Session, args: ListArgsSchema) -> int:
        """
        获取记录数
        :param db:
        :param args:
        :return:
        """
        filters = []
        if hasattr(self.Model, 'is_deleted'):
            filters.append(~self.Model.is_deleted)
        filters.extend(self.handle_list_filters(args.filters))
        filters.extend(self.handle_list_customize_filters(args.customize_filters))
        return db.query(self.Model).filter(*filters).count()

    async def list(self, db: Session, args: ListArgsSchema) -> RespListSchema:
        """
        数据列表
        :param db:
        :param args: 聚合参数，详见：ListArgsSchema
        :return: 返回数据列表结构，详见：RespListSchema
        :param args:
        :return:
        """
        filters = []
        if hasattr(self.Model, 'is_deleted'):
            filters.append(~self.Model.is_deleted)
        filters.extend(self.handle_list_filters(args.filters))
        filters.extend(self.handle_list_customize_filters(args.customize_filters))
        # 执行：数据检索
        query = db.query(self.Model).filter(*filters)
        count = query.count()
        obj_list = []
        if count > 0:
            orders = self.handle_list_orders(args.orders)
            obj_list = query.order_by(*orders).offset((args.page - 1) * args.size).limit(args.size).all()
        resp = RespListSchema()
        resp.page = args.page
        resp.size = args.size
        resp.total = count
        resp.page_count = math.ceil(count / args.size)  # 计算总页数
        resp.result = self.handle_list_keys(args.keys, obj_list)  # 处理list
        return resp

    def handle_list_filters(self, args_filters: Optional[List[ListFilterSchema]]) -> List:
        """
        查询条件组装
        :param args_filters:
        :return:
        """
        filters = []
        if args_filters:
            for item in args_filters:
                if hasattr(self.Model, item.key):
                    attr = getattr(self.Model, item.key)
                    if item.condition == '=':
                        filters.append(attr == item.value)
                    elif item.condition == '!=':
                        filters.append(attr != item.value)
                    elif item.condition == '<':
                        filters.append(attr < item.value)
                    elif item.condition == '>':
                        filters.append(attr > item.value)
                    elif item.condition == '<=':
                        filters.append(attr <= item.value)
                    elif item.condition == '>=':
                        filters.append(attr >= item.value)
                    elif item.condition == 'like':
                        filters.append(attr.like('%' + item.value + '%'))
                    elif item.condition == 'in':
                        filters.append(attr.in_(item.value.split(',')))
                    elif item.condition == '!in':
                        filters.append(~attr.in_(item.value.split(',')))
                    elif item.condition == 'null':
                        filters.append(attr.is_(None))
                    elif item.condition == '!null':
                        filters.append(~attr.is_(None))
                    elif item.condition == 'between':
                        filters.append(attr.between(item.value[0], item.value[1]))
        return filters

    def handle_list_customize_filters(self, args_filters: List[ListCustomizeFilterSchema]) -> List:
        """
        负责的一些负责的查询，自己定义
        :param args_filters:
        :return:
        """
        ...
        return []

    def handle_list_orders(self, args_orders: Optional[List[ListOrderSchema]]) -> List:
        """
        处理list接口传入的排序条件
        :param args_orders: 传入排序条件
        :return: 转换后的sqlalchemy排序条件
        """
        orders = []
        if args_orders:
            for item in args_orders:
                if hasattr(self.Model, item.key):
                    attr = getattr(self.Model, item.key)
                    if item.condition == 'desc':
                        orders.append(attr.desc())
                    elif item.condition == 'asc':
                        orders.append(attr)
                    elif item.condition == 'rand':  # 随机排序
                        orders.append(func.rand())
        return orders

    def handle_list_keys(self, args_keys: Optional[List[ListKeySchema]], obj_list: List[Model]) -> List[dict]:
        """
        处理list返回数据，根据传入参数keys进行过滤
        :param args_keys: 传入过滤字段
        :param obj_list:
        :return: 转换后的list数据，数据转为dict类型
        """
        keys = []

        if args_keys:
            for item in args_keys:
                if hasattr(self.Model, item.key):
                    keys.append(item)

        resp_list = []

        for obj in obj_list:
            dict_1 = obj.to_dict()
            # 判断：keys存在，不存在则返回所有字段
            if keys:
                dict_2 = {}
                for item in keys:
                    if item.rename:
                        dict_2[item.rename] = dict_1[item.key]
                    else:
                        dict_2[item.key] = dict_1[item.key]
            else:
                dict_2 = dict_1

            resp_list.append(dict_2)

        return resp_list
