# encoding: utf-8
"""
@project: djangoModel->thread_v2
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis:
@created_time: 2022/7/29 15:11
"""

from django.db.models import F

from ..models import Thread, ThreadExtendField
from ..services.thread_extend_service import ThreadExtendService, ThreadMainExtendService
from ..services.thread_statistic_service import StatisticsService
from ..utils.custom_tool import format_params_handle, force_transform_type, filter_fields_handler, dynamic_load_class, \
    write_to_log


class ThreadItemService:
    """
    信息表新增、修改、详情服务
    """
    thread_fields = [i.name for i in Thread._meta.fields] + ["category_id", "classify_id", "show_id"]
    extend_fields = [i.get("field") for i in list(ThreadExtendField.objects.values("field").distinct())]

    @staticmethod
    def add(params: dict = None, **kwargs):
        """
        信息添加
        :param params: 添加参数子字典
        :param kwargs:
        :return:
        """
        # 参数整合与空值验证
        params, is_void = force_transform_type(variable=params, var_type="dict", default={})
        kwargs, is_void = force_transform_type(variable=kwargs, var_type="dict", default={})
        params.update(kwargs)
        category_id, err = force_transform_type(variable=params.get("category_id"), var_type="int")
        if not category_id:
            return None, "category_id 必填"
        # 过滤主表修改字段
        try:
            # 获取主表扩展字段的过滤列表，迎着字典
            main_extend_service = ThreadMainExtendService(category_id=category_id)
            (filter_filed_list, alias_dict), err = main_extend_service.format_params_beforehand()
            alias_dict.update({"thread_price": "price"})
            # 主表的数据
            main_form_data = format_params_handle(
                param_dict=params.copy(),
                is_remove_empty=True,
                filter_filed_list=filter_filed_list + [
                    "is_deleted|bool",
                    "category_id|int",
                    "classify_id|int",
                    "show_id|int",
                    "user_id|int",
                    "with_user_id|int",
                    "title",
                    "subtitle",
                    "content",
                    "summary",
                    "access_level|int",
                    "author",
                    "ip",
                    "has_enroll|bool",
                    "has_fee|bool",
                    "has_comment|bool",
                    "has_location|bool",
                    "cover",
                    "photos|dict",
                    "video",
                    "files|dict",
                    # "price|float",
                    "thread_price|float",
                    "is_original|bool",
                    "link",
                    "create_time|date",
                    "update_time|date",
                    "publish_time|date",
                    "logs|dict",
                    "more|dict",
                    "sort|int",
                    "language_code",
                    "is_subitem_thread|int",
                    "main_thread_id|int",
                    "region_code",
                    "group_id",
                    "transact_no"
                ],
                alias_dict=alias_dict,
                is_validate_type=True
            )

            main_form_data, err = main_extend_service.validate(params=main_form_data)
            if err:
                return None, err

        except ValueError as e:
            # 模型字段验证
            return None, str(e)

        # 必填参数校验
        must_keys = ["category_id", "user_id"]
        for i in must_keys:
            if not params.get(i, None):
                return None, str(i) + " 必填"
        # IO操作
        try:
            # 主表插入数据
            instance = Thread.objects.create(**main_form_data)
            # 扩展表 插入或更新
            add_extend_res, err = ThreadExtendService.create_or_update(params, instance.id)
        except Exception as e:
            return None, f'''{str(e)} in "{str(e.__traceback__.tb_frame.f_globals["__file__"])}" : Line {str(e.__traceback__.tb_lineno)}'''

        return {"id": instance.id, "title": instance.title}, None

    @staticmethod
    def detail(pk: int = None, filter_fields: "str|list" = None, search_params: dict = None, sort: str = None):
        """
        获取信息内容
        :param sort: 排序字段
        :param search_params: 搜索参数
        :param filter_fields: 搜索结果字段过滤
        :param pk: 信息表主键搜索
        :return: data_dict,err
        """
        # 类型转换，判断是否是有效的int类型
        search_params, is_void = force_transform_type(variable=search_params, var_type="only_dict")
        pk, is_void = force_transform_type(variable=pk, var_type="int")
        if pk is None and search_params is None:
            return None, "数据不存在"
        # 田间搜索的情况
        if not pk and search_params:
            category_id, is_void = force_transform_type(variable=search_params.get("category_id"), var_type="int")
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
            search_params = format_params_handle(
                param_dict=search_params,
                filter_filed_list=filter_filed_list + [
                    "category_id|int", "category_name", "category_value", "category_id_list|list",
                    "category_parent_id|int", "platform_code",
                    "classify_id|int", "classify_name", "classify_value", "classify_id_list|list",
                    "classify_parent_id|int", "show_value",
                    "user_id|int", "user_id_list|list", "id_list|list",
                    "title", 'region_code', "create_time_start|date", "create_time_end|date", "access_level",
                    "has_enroll", "has_fee", "has_comment", "need_auth", "transact_no"
                ],
                alias_dict=alias_dict,
                split_list=["id_list", "category_id_list", "classify_id_list", "user_id_list"],
                is_remove_empty=True,
            )

        # 检查受否是有效的信息ID
        if pk:
            main_info = Thread.objects.filter(id=pk).values("id", "title", "category_id", "classify_id").first()
        else:
            sort = sort if sort in [
                "id", "title", "category_id", "classify_id"
            ] else "-id"
            main_info = Thread.objects.filter(**search_params).order_by(sort).values("id", "title", "category_id",
                                                                                     "classify_id").first()
        if not main_info:
            return None, "数据不存在"

        # 获取主表扩展字段的过滤列表以及字段映射字典
        main_extend_service = ThreadMainExtendService(category_id=main_info.get("category_id"))
        (filter_filed_list, alias_dict), err = main_extend_service.format_params_beforehand()

        # 主表字段过滤
        main_filter_fields = filter_fields_handler(
            input_field_expression=filter_fields,
            all_field_list=ThreadItemService.thread_fields + list(alias_dict.values()) + [
                "category_value", "category_name", "category_platform_code",
                "classify_value", "classify_name", "show_value", "show_name"
            ]
        )
        main_filter_fields = list(set(main_filter_fields + ["id", "user_id", "category_id", "classify_id", "show_id"]))

        # =================== section  构建ORM  ==============================
        if pk:
            thread_obj = Thread.objects.filter(id=pk)
        else:
            thread_obj = Thread.objects.filter(**search_params)

        thread_dict = thread_obj.filter(is_deleted=False).extra(select={
            'update_time': 'DATE_FORMAT(update_time, "%%Y-%%m-%%d %%H:%%i:%%s")',
            'create_time': 'DATE_FORMAT(create_time, "%%Y-%%m-%%d %%H:%%i:%%s")'
        }).annotate(
            category_value=F("category__value"),
            category_name=F("category__name"),
            category_platform_code=F("category__platform_code"),
            classify_value=F("classify__value"),
            classify_name=F("classify__name"),
            show_value=F("show__value"),
            show_name=F("show__name"),
        ).values(*main_filter_fields).first()

        # 信息统计表更新数据
        if not thread_dict:
            return None, "数据不存在"

        # 扩展字段还原
        thread_dict = format_params_handle(
            param_dict=thread_dict,
            alias_dict={v: k for k, v in alias_dict.items()}
        )
        pk = thread_dict.get("id")
        # ===================  section 构建ORM  ==============================

        # ============ section 拼接扩展数据 start ============
        # 扩展表
        extend_info, err = ThreadExtendService.get_extend_info(
            thread_id_list=[pk]
        )
        if isinstance(extend_info, list) and len(extend_info) == 1:
            thread_dict.update(extend_info[0])

        # 统计表
        statistic_list = StatisticsService.statistic_list(id_list=[pk])
        if isinstance(statistic_list, list) and len(statistic_list) == 1:
            thread_dict.update(statistic_list[0])

        # 用户详细信息表
        DetailInfoService, import_err = dynamic_load_class(import_path="xj_user.services.user_detail_info_service",
                                                           class_name="DetailInfoService")
        if not import_err:
            try:
                user_info_dict, err = DetailInfoService.get_detail(user_id=thread_dict.get("user_id", None))
                if isinstance(user_info_dict, dict):
                    thread_dict.update(user_info_dict)
            except Exception as e:
                write_to_log(prefix="信息详情接口拼接用户详细信息异常", err_obj=e)

        # 拼接定位信息
        LocationService, import_err = dynamic_load_class(import_path="xj_location.services.location_service",
                                                         class_name="LocationService")
        if not import_err:
            try:
                location_list, err = LocationService.location_list(
                    params={"thread_id_list": [pk]},
                    need_pagination=False,
                    filter_fields=[
                        "name", "thread_id", "region_code", "longitude", "latitude", "altitude", "coordinate_type"
                    ]
                )
                if isinstance(location_list, list) and len(location_list) == 1 and isinstance(location_list[0], dict):
                    thread_dict.update(location_list[0])
            except Exception as e:
                write_to_log(prefix="信息详情接口拼接定位信息异常", err_obj=e)
        # ============ section 拼接扩展数据 end  ============

        # 所有访问成功，则进行统计计数
        StatisticsService.increment(thread_id=pk, tag='views', step=1)

        # 过滤字段
        filter_fields_thread_dict = format_params_handle(
            param_dict=thread_dict,
            is_remove_null=False,
            filter_filed_list=filter_fields_handler(
                input_field_expression=filter_fields,
                default_field_list=list(thread_dict.keys())
            ),
            remove_filed_list=["field_1", "field_2", "field_3", "field_4", "field_5", "field_6", "field_7", "field_8",
                               "field_9", "field_10"]
        )
        return filter_fields_thread_dict, None

    @staticmethod
    def edit(params: dict = None, pk: int = None, **kwargs):
        """
        信息编辑服务
        :param params: 信息编辑的字段
        :param pk: 信息表需要修改的主键
        :return: instance，err
        """
        # 参数校验
        params, is_void = force_transform_type(variable=params, var_type="dict", default={})
        kwargs, is_void = force_transform_type(variable=kwargs, var_type="dict", default={})
        params.update(kwargs)
        if not params:
            return None, None
        # 获取要修改的信息主键ID
        pk, is_void = force_transform_type(variable=pk or params.pop("id", None), var_type="int")
        if not pk:
            return None, "不是一个有效的pk"
        # 检查受否是有效的信息ID
        main_res = Thread.objects.filter(id=pk)
        main_info = main_res.values("id", "title", "category_id", "classify_id").first()
        if not main_info:
            return None, "数据不存在，无法进行修改"

        # =================  过滤主表修改字段和扩展表修改字段  start ==============================
        # 获取主表扩展字段的过滤列表以及字段映射字典
        main_extend_service = ThreadMainExtendService(category_id=main_info.get("category_id"))
        (filter_filed_list, alias_dict), err = main_extend_service.format_params_beforehand()

        main_form_data = format_params_handle(
            params.copy(),
            filter_filed_list=filter_filed_list + [
                "is_deleted|int", "title", "subtitle", "content", "summary", "access_level|int", "author", "ip",
                "has_enroll|int", "has_fee|int", "has_comment|int", "has_location|int", "cover", "photos|dict", "video",
                "files|dict", "price|float",
                "is_original|int", "link", "create_time|date", "update_time|date", "logs", "more", "sor|int",
                "language_code", "show_id|int", "category_id|int", "classify_id|int", "user_id|int", "with_user_id|int",
                "is_subitem_thread|int", "main_thread_id|int"
            ],
            alias_dict=alias_dict
        )
        # =================  过滤主表修改字段和扩展表修改字段  end    ==============================

        # ========================  IO操作  start ==================================
        try:
            # 主表修改
            if main_form_data:
                main_res.update(**main_form_data)  # 主表修改

            # 扩展数据修改
            data, err = ThreadExtendService.create_or_update(params.copy(), pk,
                                                             main_form_data.get("category_id", None))  # 扩展字段修改
            if err:
                return None, err

            return None, None
        except Exception as e:
            return None, "msg:" + "信息主表写入异常：" + str(e) + "  line:" + str(
                e.__traceback__.tb_lineno) + ";tip:参数格式不正确，请参考服务文档使用"
        # ========================  IO操作  end    ==================================

    @staticmethod
    def delete(pk: int = None):
        """
        软删除信息
        :param pk: 主键ID
        :return: None,err
        """
        pk, is_void = force_transform_type(variable=pk, var_type="int")
        if not pk:
            return None, "非法请求"
        main_res = Thread.objects.filter(id=pk, is_deleted=0)
        if not main_res:
            return None, "数据不存在，无法进行删除"

        main_res.update(is_deleted=1)
        return None, None
