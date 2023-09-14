# encoding: utf-8
"""
@project: djangoModel->thread_category_item_service
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 类别单条服务
@created_time: 2022/10/25 14:21
"""
from django.core.paginator import Paginator
from django.db.models import F, Q

from ..models import ThreadCategory
from ..services.thread_category_tree_service import ThreadCategoryTreeServices
from ..utils.custom_tool import format_params_handle, filter_fields_handler, force_transform_type


class ThreadCategoryService():
    @staticmethod
    def edit(params: dict = None, pk: int = None, search_params: dict = None):
        """
        类别修改
        :param params: 修改参数
        :param pk: 主键修改
        :param search_params: 批量修改入口
        :return: data, err
        """
        # 参数初始化
        if params is None and not isinstance(params, dict):
            params = {}
        try:
            pk = int(pk)
        except TypeError:
            pk = None
        # 判断是否存在可编辑得到参数
        if not pk and not search_params:
            return None, "没有可编辑的数据"
        params = format_params_handle(
            param_dict=params,
            is_remove_null=True,
            is_remove_empty=False,
            filter_filed_list=["platform_code", "value", "name", "need_auth", "description", "sort", "parent_id"]
        )
        # 搜索可修改的数据
        category_obj = ThreadCategory.objects
        if pk:
            category_obj = category_obj.filter(id=pk)
        if search_params:
            category_obj = category_obj.filter(**search_params)
        # 不存在可修改的类别
        if not category_obj:
            return None, "没找到可修改的数据"
        instance = category_obj.update(**params)
        return instance, None

    @staticmethod
    def delete(pk: int = None, search_params: dict = None):
        if not pk and not search_params:
            return None, "没有可删除的数据"
        # 搜索可修改的数据
        category_obj = ThreadCategory.objects
        if pk:
            category_obj = category_obj.filter(id=pk)
        if search_params:
            category_obj = category_obj.filter(**search_params)

        if not category_obj:
            return None, "没找到可删除的数据"
        category_obj.update(is_deleted=1)
        return None, None

    @staticmethod
    def add(params: dict = None):
        """
        添加类别接口服务
        :param params:dict 添加参数字典
        :return: None,err
        """
        if not params or not isinstance(params, dict):
            return None, "不是有效的参数"

        params['parent_id'] = None if not params.get("parent_id") else params.get("parent_id")
        params['platform_code'] = None if not params.get("platform_code") else params.get("platform_code")

        filtered_add_params = format_params_handle(
            param_dict=params,
            filter_filed_list=["id", "platform_code", "value", "name", "need_auth", "description", "sort", "parent_id", ],
            is_remove_null=True
        )

        add_category_value = filtered_add_params.get("value")
        if not add_category_value:
            return None, "类别唯一值（value）必填"

        category_set = ThreadCategory.objects.filter(value=add_category_value).first()
        if category_set:
            return None, "该value已经存在，请勿重复添加"

        try:
            filtered_add_params['is_deleted'] = False
            instance = ThreadCategory.objects.create(**filtered_add_params)
        except Exception as e:
            return None, str(e)
        return instance.to_json(), None

    @staticmethod
    def list(params: dict = None, filter_fields: "str|list" = None, need_pagination: bool = True, need_child: bool = None):
        """
        类别。类似于版块大类的概念.
        用于圈定信息内容所属的主要类别
        :param params: 搜索参数
        :param filter_fields: 过滤字段
        :param need_pagination: 是否需要分页
        :param need_child: 是否查询该类别树下面的所有子类别
        :return: data,err
        """
        # 参数筛选
        params, err = force_transform_type(variable=params, var_type="dict", default={})
        need_pagination, err = force_transform_type(variable=need_pagination, var_type="bool", default=False)
        sort = params.pop("sort", "-id")
        sort = sort if sort and sort in ["-id", "-sort", "id", "sort"] else "-id"
        page, err = force_transform_type(variable=params.pop("page", 1), var_type="int", default=1)
        size, err = force_transform_type(variable=params.pop("size", 10), var_type="int", default=10)
        # 是否查询子节点,分类的数量并不多所以可以进行where in 搜索。
        if not need_child is None:
            category_id = params.pop("id", None)
            category_value = params.pop("category_value", None)
            if category_value or category_id:
                params["id_list"], err = ThreadCategoryTreeServices.get_child_ids(
                    category_id=category_id,
                    category_value=category_value
                )

        # 查询参数过滤，替换
        params = format_params_handle(
            param_dict=params,
            filter_filed_list=["id", "id_list", "platform_code", "value", "category_value", "name", "need_auth", "description", "parent_id", "parent_value"],
            alias_dict={"name": "name__contains", "value": "category_value", "id_list": "id__in"}
        )
        # 查询字段处理，得出可以返回字段列表
        filter_fields_list = filter_fields_handler(
            default_field_list=["id", "platform_code", "category_value", "name", "need_auth", "description", "sort", "parent_value", "parent_id", "is_deleted", "config"],
            input_field_expression=filter_fields
        )

        # 数据库orm查询
        category_set = ThreadCategory.objects.filter(Q(is_deleted__isnull=True) | Q(is_deleted=0)).annotate(
            category_value=F('value'),
            parent_value=F("parent__value")
        ).order_by(sort)
        category_set = category_set.filter(**params)
        thread_category_obj = category_set.values(*filter_fields_list)

        # 不需要分页展示全部数据
        if not need_pagination:
            if not thread_category_obj:
                return [], None
            return list(thread_category_obj), None

        # 分页展示
        count = thread_category_obj.count()
        finish_set = list(Paginator(thread_category_obj, size).page(page))
        return {'size': int(size), 'page': int(page), 'total': count, 'list': finish_set}, None
