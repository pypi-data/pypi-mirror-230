# encoding: utf-8
"""
@project: djangoModel->thread_v2
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis:
@created_time: 2022/7/29 15:11
"""
import logging
import re

from django.core.paginator import Paginator, EmptyPage
from django.db.models import F

from ..models import Thread, ThreadTagMapping, ThreadExtendField
from ..services.thread_extend_service import ThreadExtendService, ThreadMainExtendService
from ..utils.custom_tool import filter_result_field, format_params_handle, force_transform_type, filter_fields_handler
from ..utils.join_list import JoinList

log = logging.getLogger()


# 信息服务CURD(支持扩展字段配置)
class ThreadListService:
    thread_fields = [i.name for i in Thread._meta.fields] + ["category_id", "classify_id", "show_id"]
    extend_fields = [i.get("field") for i in list(ThreadExtendField.objects.values("field").distinct())]
    all_fields = [
        "id", "is_deleted", "category_id", "classify_id", "show_id", "region_code", "user_id", "with_user_id",
        "group_id", "transact_no", "title", "subtitle",
        "content", "summary", "access_level", "author", "ip", "has_enroll", "has_fee", "has_comment", "has_location",
        "cover", "photos", "video", "files", "price", "is_original", "link", "create_time", "update_time", "logs",
        "more", "sort",
        "language_code", "is_subitem_thread", "main_thread", "category_value", "category_name", "need_auth",
        "classify_value", "classify_name", "show_value", "field_1", "field_2", "field_3", "field_4",
        "field_5", "field_6", "field_7", "field_8", "field_9", "field_10", "field_11", "field_12", "field_13",
        "field_14", "field_15",
    ]

    @staticmethod
    def list(params=None, need_pagination: bool = True, filter_fields=None, **kwargs):
        """
        信息列表
        @param params 筛选条件
        @param need_pagination: 是否分页
        @param filter_fields: 过滤字段
        """
        # ================== section 参数处理 start ==================
        params, is_void = force_transform_type(variable=params, var_type="dict", default={})
        kwargs, is_void = force_transform_type(variable=kwargs, var_type="dict", default={})
        params.update(kwargs)
        page, is_void = force_transform_type(variable=params.pop('page', 1), var_type="int", default=1)
        size, is_void = force_transform_type(variable=params.pop('size', 10), var_type="int", default=10)
        need_pagination, is_void = force_transform_type(variable=need_pagination, var_type="bool", default=True)
        if int(size) > 100:
            size = 10

        sort = params.pop('sort', None)
        sort = sort if sort and sort in ['id', '-id', 'sort', '-sort', 'create_time', '-create_time', 'update_time',
                                         '-update_time'] else "-id"

        exclude_category_list = params.pop('exclude_category_list').split(',') if params.get(
            'exclude_category_list') else None

        # 定位搜索行政区划编码 因为长度可能不统一，兼容处理使用正则匹配。
        region_code, is_void = force_transform_type(variable=params.pop("region_code", None), var_type="int")
        if region_code:
            params["region_code"] = re.sub("0.$", "", str(region_code))

        filter_fields = filter_fields_handler(
            input_field_expression=filter_fields,
            all_field_list=ThreadListService.all_fields
        )
        # ---------------------- section index2 主表扩展处理 start --------------------------
        category_id, is_void = force_transform_type(variable=params.get("category_id"), var_type="int")
        filter_filed_list = []
        alias_dict = {}
        if category_id:
            main_extend_service = ThreadMainExtendService(category_id=category_id)
            (filter_filed_list, alias_dict), err = main_extend_service.format_params_beforehand()

        alias_dict.update({
            "id_list": "id__in",
            "user_id_list": "user_id__in",
            "category_id_list": "category_id__in",
            "category_value": "category__value",
            "category_parent_id": "category__parent_id",
            "platform_code": "category__platform_code",
            "classify_value": "classify__value",
            "classify_id_list": "classify__in",
            "classify_parent_id": "classify__parent_id",
            "title": "title__contains",
            "create_time_start": "create_time__gte",
            "create_time_end": "create_time__lte",
            "region_code": "region_code__regex"
        })
        # ---------------------- section index2 主表扩展处理 end --------------------------
        # 允许进行过渡的字段条件
        conditions = format_params_handle(
            param_dict=params,
            filter_filed_list=filter_filed_list + [
                "category_id|int", "category_name", "category_value", "category_id_list|list", "category_parent_id|int",
                "platform_code",
                "classify_id|int", "classify_name", "classify_value", "classify_id_list|list", "classify_parent_id|int",
                "show_value",
                "user_id|int", "user_id_list|list", "id_list|list",
                "title", 'region_code', "create_time_start|date", "create_time_end|date", "access_level", "has_enroll",
                "has_fee", "has_comment", "need_auth", "is_subitem_thread", "transact_no"
            ],
            alias_dict=alias_dict,
            split_list=["id_list", "category_id_list", "classify_id_list", "user_id_list"],
            is_remove_empty=False,
        )
        # ================== section 参数处理 end ==================

        # ==================== section 数据检索 start ====================
        # 标签搜索
        # TODO 修改建议修改主表，使用外键查询。
        tag_id_list = params.get('tag_id_list') if params.get('tag_id_list') else None
        if tag_id_list:
            try:
                id_list = params.pop("id_list", None)
                if not id_list or not isinstance(id_list, list):
                    id_list = []
                params["id_list"] = list(
                    set(id_list + ThreadTagMapping.objects.filter(tag_id__in=tag_id_list).values_list('thread_id',
                                                                                                      flat=True)))
            except ValueError as e:
                log.error(f'信息表标签查询{e}')

        thread_set = Thread.objects.order_by(sort)
        # 指定不需要过滤的类别字段
        if exclude_category_list:
            thread_set = thread_set.exclude(category_id__in=exclude_category_list)
        # 开始按过滤条件
        try:
            thread_set = thread_set.extra(select={
                'create_time': 'DATE_FORMAT(create_time, "%%Y-%%m-%%d %%H:%%i:%%s")',
                'update_time': 'DATE_FORMAT(update_time, "%%Y-%%m-%%d %%H:%%i:%%s")'
            }).annotate(
                category_value=F("category_id__value"),
                category_name=F("category_id__name"),
                need_auth=F("category_id__need_auth"),
                classify_value=F("classify_id__value"),
                classify_name=F("classify_id__name"),
                show_value=F("show_id__value")
            )
            # 注意：为空和0认为是未删除的数据，为1代表删除的
            print(conditions)
            thread_set = thread_set.exclude(is_deleted=True).filter(**conditions).values(*filter_fields)
            count = thread_set.count()
        except Exception as e:
            return None, "err:" + e.__str__() + "line:" + str(e.__traceback__.tb_lineno)

        # 不需要分页
        if not need_pagination and count <= 100:
            finish_list = list(thread_set)
            # 主表扩展字段替换
            finish_list, err = ThreadMainExtendService.replace_list_extend(finish_list)
            # 获取扩展标字段
            thread_id_list = list(set([item['id'] for item in finish_list if item['id']]))
            thread_extend_list, err = ThreadExtendService.get_extend_info(thread_id_list=thread_id_list)
            JoinList(finish_list, thread_extend_list, l_key="id", r_key="thread_id").join()

            return finish_list, None

        # 分页数据
        paginator = Paginator(thread_set, size)
        try:
            paginator_set = paginator.page(page)
        except EmptyPage:
            paginator_set = paginator.page(paginator.num_pages)
        finish_set = list(paginator_set.object_list)
        # ==================== section 数据检索 end ====================

        # ================= section 扩展数据拼接  start =================
        # 主表扩展字段替换
        finish_set, err = ThreadMainExtendService.replace_list_extend(finish_set)
        # 扩展表字段
        thread_id_list = list(set([item['id'] for item in finish_set if item['id']]))
        thread_extend_list, err = ThreadExtendService.get_extend_info(thread_id_list=thread_id_list)
        if err:
            return None, err
        JoinList(finish_set, thread_extend_list, l_key="id", r_key="thread_id").join()
        # ================= section 扩展数据拼接  end  =================
        return {'size': int(size), 'page': int(page), 'total': count, 'list': finish_set}, None

    @staticmethod
    def search(id_list: list = None, need_map: bool = False, filter_fields: "list|str" = None):
        """
        按照ID搜索信息
        :param id_list: 信息ID列表
        :param need_map: True: {"thead_id":thread_item,...}, False: [thread_item,....]
        :param filter_fields: 过滤字段
        :return: data, err
        """
        id_list, is_void = force_transform_type(variable=id_list, var_type="list")
        if not id_list:
            return [], None
        # 主表select字段筛选
        main_filter_fields = filter_fields_handler(
            input_field_expression=filter_fields,
            all_field_list=ThreadListService.thread_fields + [
                "thread_category_value", "thread_category_name", "category_value", "category_name",
                "need_auth", "thread_classify_value", "thread_classify_name", "classify_value",
                "classify_name", "show_value"
            ]
        )
        main_filter_fields = list(set(main_filter_fields + ["id", "category_id", "classify_id", "show_id"]))
        # 开始按过滤条件
        thread_set = Thread.objects.filter(id__in=id_list).extra(select={
            "create_time": 'DATE_FORMAT(create_time, "%%Y-%%m-%%d %%H:%%i:%%s")',
            "update_time": 'DATE_FORMAT(update_time, "%%Y-%%m-%%d %%H:%%i:%%s")',
        })
        try:
            thread_set = thread_set.annotate(
                thread_category_value=F("category_id__value"),
                thread_category_name=F("category_id__name"),
                category_value=F("category_id__value"),
                category_name=F("category_id__name"),
                need_auth=F("category_id__need_auth"),
                thread_classify_value=F("classify_id__value"),
                thread_classify_name=F("classify_id__name"),
                classify_value=F("classify_id__value"),
                classify_name=F("classify_id__name"),
                show_value=F("show_id__value")
            )
            thread_set = thread_set.filter(is_deleted=0)
            # TODO 后期迭代计划：删除调thread前缀，与前端沟通一致 2023/3/29
            thread_set = thread_set.values(*main_filter_fields)
        except Exception as e:
            return None, "err:" + e.__str__()
        thread_set = list(thread_set)
        # 主表扩展字段替换
        thread_set, err = ThreadMainExtendService.replace_list_extend(thread_set)

        # ================= 扩展数据拼接  start=================
        extend_filed_fields = filter_fields_handler(
            input_field_expression=filter_fields,
            all_field_list=ThreadListService.extend_fields
        )
        if extend_filed_fields:
            thread_extend_list, err = ThreadExtendService.get_extend_info(
                thread_id_list=list(set([item['id'] for item in thread_set if item['id']]))
            )
            thread_extend_list = filter_result_field(
                result_list=thread_extend_list,
                filter_filed_list=list(set(extend_filed_fields + ["thread_id"]))
            )
            JoinList(thread_set, thread_extend_list, l_key="id", r_key="thread_id").join()
        # ================= 扩展数据拼接  end  =================

        # 由于有字段冲突，所以这里做一次字段别名处理
        finish_set = filter_result_field(
            result_list=thread_set,
            alias_dict={"price": "thread_price", "category": "category_id", "classify": "classify_id"},
        )
        # 以字典形式返回{"主键"：{数据...}}
        need_map, is_void = force_transform_type(variable=need_map, var_type="bool", default=False)
        if need_map:
            finish_set = {i['id']: i for i in finish_set}
        return finish_set, None

    @staticmethod
    def search_ids(search_prams: dict = None, is_strict_mode: bool = False):
        """
        根据搜索条件查search_prams，询信息表ID
        :param is_strict_mode: 是否严格模式，如果严格模式则超过100条则不返回。非严格模式则进行返回前100条
        :param search_prams: 搜素参数
        :return: list, err
        """
        search_prams, is_void = force_transform_type(variable=search_prams, var_type="dict", default={})
        # 定位搜索 因为长度可能不统一，兼容处理使用正则匹配。
        region_code, is_void = force_transform_type(variable=search_prams.pop("region_code", None), var_type="int")
        if region_code:
            search_prams["region_code"] = re.sub("0.$", "", str(region_code))
        # 用于条件搜索
        search_prams = format_params_handle(
            param_dict=search_prams,
            filter_filed_list=[
                "title", "user_id", "subtitle", "access_level", "author",
                "has_enroll", "has_fee", "has_comment", "has_location", "is_original", "finance_invoicing_code",
                "category_value", "classify_value"  "thread_category_value", "thread_classify_value",
                "platform_code", "need_auth", "show_value", "region_code"
            ],
            alias_dict={
                "title": "title__contains", "subtitle": "subtitle__contains", "region_code": "region_code__regex"
            },
            is_remove_empty=True
        )
        if not search_prams:
            return [], None
        thread_set = Thread.objects
        try:
            thread_set = thread_set \
                .annotate(thread_category_value=F("category__value")) \
                .annotate(category_value=F("category__value")) \
                .annotate(platform_code=F("category__platform_code")) \
                .annotate(need_auth=F("category__need_auth")) \
                .annotate(thread_classify_value=F("classify__value")) \
                .annotate(classify_value=F("classify__value")) \
                .annotate(show_value=F("show__value")).filter(is_deleted=0)
            thread_set = thread_set.filter(**search_prams)
            count = thread_set.count()

            # 严格模式进行查询保护，如果筛选条件超出100条,则不返回。
            if count >= 100 and is_strict_mode:
                return [], None
            thread_set = thread_set.values('id')

            # 如果非严格模式，则取前100条
            if count >= 100 and not is_strict_mode:
                thread_set = Paginator(thread_set, 100).page(1)
                thread_set = list(thread_set.object_list)
        except Exception as e:
            return None, "err:" + e.__str__()

        # 返回ID序列
        thread_id_list = [i["id"] for i in list(thread_set)]
        return thread_id_list, None
