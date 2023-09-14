# encoding: utf-8
"""
@project: djangoModel->thread_category_item_service
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 类别单条服务
@created_time: 2022/10/25 14:21
"""

from django.core.paginator import Paginator
from django.db.models import F

from ..models import ThreadClassify
from ..services.thread_category_tree_service import ThreadCategoryTreeServices
from ..utils.custom_tool import format_params_handle, filter_fields_handler, force_transform_type


class ThreadClassifyService():
    classify_fields = [i.name for i in ThreadClassify._meta.fields] + ["category_id"]

    @staticmethod
    def edit(params: dict = None, pk: int = None, search_params: dict = None, **kwargs):
        # 类型检查，强制类转换
        params, is_pass = force_transform_type(variable=params, var_type="dict", default={})
        kwargs, is_pass = force_transform_type(variable=kwargs, var_type="dict", default={})
        params.update(kwargs)
        search_params, is_pass = force_transform_type(variable=search_params, var_type="dict", default={})
        pk, is_pass = force_transform_type(variable=pk, var_type="int")

        # 过滤字段安全处理
        try:
            format_params_handle(
                param_dict=params.copy(),
                is_remove_empty=False,
                is_validate_type=True,
                filter_filed_list=["value", "name", "show|int", "show_id|int", "description", "category|int", "category_id|int", "icon", "sort", "parent_id|int", "config|dict"],
                alias_dict={"category": "category_id", "show": "show_id"}
            )
        except ValueError as e:
            return None, str(e)

        params = format_params_handle(
            param_dict=params,
            is_remove_null=False,
            filter_filed_list=["value", "name", "show", "show_id", "description", "category", "category_id", "icon", "sort", "parent_id", "config"],
            alias_dict={"category": "category_id", "show": "show_id"}
        )
        if not params:
            return None, None
        if not pk and not search_params:
            return None, "没有可编辑的数据"
        # 搜索可修改的数据
        classify_obj = ThreadClassify.objects
        if pk:
            classify_obj = classify_obj.filter(id=pk)
        if search_params:
            classify_obj = classify_obj.filter(**search_params)
        # 判断是否存在编辑对象
        if not classify_obj:
            return None, "没找到可修改的数据"
        instance = classify_obj.update(**params)
        return instance, None

    @staticmethod
    def delete(pk=None, search_params=None):
        search_params, is_pass = force_transform_type(variable=search_params, var_type="dict")
        pk, is_pass = force_transform_type(variable=pk, var_type="int")
        if not pk and not search_params:
            return None, "没有可删除的数据"
        # 搜索可修改的数据
        classify_obj = ThreadClassify.objects
        if pk:
            classify_obj = classify_obj.filter(id=pk)
        if search_params:
            classify_obj = classify_obj.filter(**search_params)

        if not classify_obj:
            return None, "没找到可删除的数据"
        classify_obj.delete()
        return None, None

    @staticmethod
    def add(params: dict = None, **kwargs):
        """
        信息列表添加
        :param params: 添加字典参数
        :return: None, err
        """
        # 强制类型转换，参数合并
        params, is_pass = force_transform_type(variable=params, var_type="dict", default={})
        kwargs, is_pass = force_transform_type(variable=kwargs, var_type="dict", default={})
        params.update(kwargs)
        try:
            format_params_handle(
                param_dict=params,
                filter_filed_list=["value", "name", "show|int", "show_id|int", "description", "category|int", "category_id|int", "icon", "sort|int", "parent_id|int", "config|json"],
                alias_dict={"category": "category_id"},
                is_remove_empty=True
            )
        except ValueError as e:
            return None, str(e)

        if not params:
            return None, "没有有效的参数"
        # 数据校验，value不为空且唯一
        classify_value = params.get("value")
        if not classify_value:
            return None, "分类唯一值（value）必填"
        classify_set = ThreadClassify.objects.filter(value=classify_value).first()
        if classify_set:
            return None, "该value已经存在，请勿重复添加"
        # ORM插入数据
        try:
            instance = ThreadClassify.objects.create(**params)
        except Exception as e:
            return None, str(e)
        return instance.to_json(), None

    @staticmethod
    def list(params: dict = None, filter_fields: list = None, need_pagination: bool = True, need_category_child: bool = False, **kwargs):
        """
        信息类别查询服务
        类别。类似于版块大类的概念，用于圈定信息内容所属的主要类别
        :param params: 搜索参数
        :param filter_fields: 过滤字段
        :param need_pagination: 是否分页
        :param need_category_child: 是否查询子类别下面所有的分类
        :return: data,err
        """
        # 参数合并与空值处理
        params, is_pass = force_transform_type(variable=params, var_type="dict", default={})
        kwargs, is_pass = force_transform_type(variable=kwargs, var_type="dict", default={})
        params.update(kwargs)
        page, is_pass = force_transform_type(variable=params.get("page", 1), var_type="int", default=1)
        size, is_pass = force_transform_type(variable=params.get("size", 10), var_type="int", default=10)
        need_pagination, err = force_transform_type(variable=need_pagination, var_type="bool", default=True)
        sort = params.get("sort", "-id")
        sort = sort if sort and sort in ["id", "sort", "-id", "-sort"] else "-id"
        # 分页参数
        # 是否类别的查询子节点
        if not need_category_child is None:
            category_id = params.pop("category_id", None)
            category_value = params.pop("category_value", None)
            if category_value or category_id:
                params["category_id_list"], err = ThreadCategoryTreeServices.get_child_ids(
                    category_id=category_id,
                    category_value=category_value
                )

        # 搜索参数过滤
        params = format_params_handle(
            param_dict=params,
            filter_filed_list=[
                "id", "value", "name", 'classify_value',
                "show_id", "show_value", "category_id", "category_id_list", "category_value", "parent_id", "parent_value"
            ],
            alias_dict={"name": "name__contains", "category_id_list": "category_id__in", 'classify_value': "value"}
        )
        # 查询字段筛选
        default_fields = [
            "id", "value", "name", "description", "show_id", "show_value", "category_id", "category_value",
            "icon", "sort", "parent_id", "parent_value", "config", "category_config", "category_name", "platform_code",
        ]
        filter_fields_list = filter_fields_handler(
            input_field_expression=filter_fields,
            default_field_list=default_fields,
            all_field_list=ThreadClassifyService.classify_fields + [
                "parent_value", "show_value", "category_config", "category_name", "platform_code", "category_value", "need_auth",
                "category_description", "category_sort", "category_parent_id", "category_is_deleted",
            ]
        )
        # 构建ORM，IO查询
        classify_set = ThreadClassify.objects.annotate(
            parent_value=F("parent__value"),
            show_value=F("show__value"),
            category_config=F("category__config"),
            category_name=F("category__name"),
            platform_code=F('category__platform_code'),
            category_value=F('category__value'),
            need_auth=F("category__need_auth"),
            category_description=F("category__description"),
            category_sort=F("category__sort"),
            category_parent_id=F("category__parent_id"),
            category_is_deleted=F("category__is_deleted"),
        ).order_by(sort)
        classify_set = classify_set.filter(**params)
        thread_classify_obj = classify_set.values(*filter_fields_list)
        # 判断分页与不分页返回
        if not need_pagination:
            # 不需要分页展示全部数据
            if not thread_classify_obj:
                return [], None
            return list(thread_classify_obj), None
        else:
            # 分页展示
            count = thread_classify_obj.count()
            finish_set = list(Paginator(thread_classify_obj, size).page(page))
            return {'size': int(size), 'page': int(page), 'total': count, 'list': finish_set}, None
