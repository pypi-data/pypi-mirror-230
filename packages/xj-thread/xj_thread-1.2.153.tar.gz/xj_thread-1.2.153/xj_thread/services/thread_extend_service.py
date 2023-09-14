# encoding: utf-8
"""
@project: djangoModel->extend_service
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 扩展服务
@created_time: 2022/7/29 15:14
"""
from django.db.models import F

from ..models import ThreadExtendField, Thread, ThreadExtendData, ThreadMainExtendField
from ..utils.custom_tool import write_to_log, force_transform_type, filter_result_field, format_params_handle


# TODO 后面的版本会删除ThreadExtendInputService 和 ThreadExtendOutPutService
# 服务提供 扩展表的字段映射关系，返回映射后KEY名。
# 达意最好是ThreadExtendInsertService:
class ThreadExtendInputService:
    thread_extend_filed = None

    def __init__(self, form_data):
        """
        :param form_data: 表单
        :param need_all_field: 是否需要全部的扩展字段（查询的时候会用到）
        """
        self.form_data = form_data
        self.form_data['category_id_id'] = self.form_data.pop("category_id", None)
        self.form_data['classify_id_id'] = self.form_data.pop("classify_id", None)
        # 新增或者修改的时候
        self.thread_extend_filed = {}
        category_id = None
        if "id" in self.form_data.keys():  # 修改时候：传了id,没有传classify_id
            category_id = Thread.objects.filter(id=self.form_data.get('id')).first().category_id

        if self.form_data.get('category_id_id', None):
            category_id = self.form_data.get('category_id_id')

        if category_id:
            self.thread_extend_filed = {
                item["field"]: item["field_index"] for item in
                ThreadExtendField.objects.filter(category_id_id=category_id).values('field', 'field_index')
            }

    # 请求参数转换
    # TODO 弃用 sieyoo
    def transform_param(self):
        # 没有定义扩展映射直接返回，不进行扩展操作
        if self.thread_extend_filed is None:
            return self.form_data, None
        extend_data = {self.thread_extend_filed[k]: self.form_data.pop(k) for k, v in self.form_data.copy().items() if
                       k in self.thread_extend_filed.keys()}
        return self.form_data, extend_data


# 所有的输出信息服务都需要有统一的公共方法
# 暂时定位 output
class ThreadExtendOutPutService():
    # extend_field:扩展数据表的字段如field_1,field_2....
    # field:配置的字段映射
    field_list = None
    extend_field_map = None  # {extend_field:field}
    field_map = None  # {field:extend_field}
    finish_data = None  # 最终完成映射的扩展数据字典

    def __init__(self, category_id_list=None, thread_id_list=None):
        if category_id_list is None:
            raise Exception("category_id_list 必传")
        if thread_id_list is None:
            raise Exception("thread_id_list 必传")
        self.category_id_list = category_id_list
        self.thread_id_list = thread_id_list

        # 字段映射关系
        self.field_list = list(ThreadExtendField.objects.values())
        self.field_map = {}  # {i["category_id"]: {i["field_index"]: i["field"],....},....}
        for item in self.field_list:
            if self.field_map.get(item["category_id"]):
                self.field_map[item["category_id"]].update({item["field_index"]: item["field"]})
            else:
                self.field_map[item["category_id"]] = {item["field_index"]: item["field"]}

    def out_put(self):
        self.finish_data = {}  # 返回 self.finish_data：{thread_id:{扩展数据},.....} {thread_id:{扩展数据},.....}
        # 获取扩展数据
        extend_data = list(ThreadExtendData.objects.filter(thread_id__in=self.thread_id_list).annotate(
            category_id=F("thread_id__category_id")).values())
        extend_data = [(i.pop("thread_id_id"), i.pop("category_id"), i) for i in extend_data]
        # 扩展数据 替换KEY
        for thread_id, category_id, item in extend_data:
            category_field = self.field_map.get(category_id, None)
            if category_field is None:
                continue
            remove_none = {k: v for k, v in item.items() if v}
            temp_dict = {}
            for k, v in remove_none.items():
                if category_field.get(k):
                    temp_dict.update({category_field[k]: v})
            self.finish_data[thread_id] = temp_dict
        return self.finish_data

    def merge(self, merge_set, merge_set_key='id'):
        # 把结果集和{thread_id:{扩展数据}}，拼接到 merge_set
        extend_map = self.out_put()
        for item in merge_set:
            if item.get(merge_set_key) and extend_map.get(item[merge_set_key]):
                item.update(extend_map[item[merge_set_key]])
        return merge_set


# 扩展字段增删改查
class ThreadExtendService:
    @staticmethod
    def create_or_update(params=None, thread_id=None, category_id=None, **kwargs):
        """
        信息表扩展信息新增或者修改
        :param params: 扩展信息，必填
        :param thread_id: 信息ID，必填
        :param category_id: 分类ID, 非必填
        :return: None，err
        """
        # 参数合并，强制类型转换
        kwargs, is_void = force_transform_type(variable=kwargs, var_type="dict", default={})
        params, is_void = force_transform_type(variable=params, var_type="dict", default={})
        params.update(kwargs)

        # 不存在信息ID 无法修改
        thread_id = thread_id or params.pop("thread_id", None)
        thread_id, is_void = force_transform_type(variable=thread_id, var_type="int")
        if thread_id is None:
            return None, "扩展字段修改错误,thread_id不可以为空"

        # 检查信息ID 是否正确
        thread_obj = Thread.objects.filter(id=thread_id).first()
        if not thread_obj:
            return None, "没有找到该主表信息，无法添加扩展信息"

        # 获取信息类别ID 当没有指定信息分类的时候，则不可以添加或者修改扩展数据。因为扩展字段于类别绑定。
        category_id = category_id if category_id else thread_obj.category_id
        if not category_id:
            return None, "没有信息指定信息类别，无法添加扩展信息"

        # 扩展字段映射, 如没有配置对应类别的扩展字段，则无法添加扩展数据。
        extend_fields = ThreadExtendField.objects.filter(category_id=category_id).values("field_index", "default",
                                                                                         "field")
        if not extend_fields:
            # 没有配置扩展该类别的扩展字段，无法添加扩展信息
            return None, None

        extend_model_fields = [i.name for i in ThreadExtendData._meta.fields if not i.name == "thread_id"]  # 扩展信息表的字段列表
        # 扩展数据替换
        extend_field_map = {item["field"]: item["field_index"] for item in extend_fields if
                            item["field_index"] in extend_model_fields}  # 得到合理的配置
        transformed_extend_params = {extend_field_map[k]: v for k, v in params.items() if
                                     extend_field_map.get(k)}  # {"自定义扩展字段":"123"} ==>> {"filed_1":"123"}
        # 修改或添加数据
        try:
            extend_obj = ThreadExtendData.objects.filter(thread_id=thread_id)
            if not extend_obj:
                # 新增的时候，启用扩展字段参数设置默认值。
                # 注意：防止后台管理员配置错误,出现数据表不存在的字段。所以需要进行一次字段排除
                default_field_map = {item["field_index"]: item["default"] for item in extend_fields if
                                     (item["default"] and item["field_index"] in extend_model_fields)}
                for field_index, default in default_field_map.items():
                    transformed_extend_params.setdefault(field_index, default)
                if not transformed_extend_params:
                    # 没有可添加的数据，请检查扩展字段的默认值配置
                    return None, None

                # 添加扩展信息
                transformed_extend_params.setdefault('thread_id_id', thread_id)
                ThreadExtendData.objects.create(**transformed_extend_params)
                return None, None
            else:
                if not transformed_extend_params:
                    # 没有可修改的数据
                    return None, None

                extend_obj.update(**transformed_extend_params)
                return None, None
        except Exception as e:
            write_to_log(prefix="信息表扩展信息新增或者修改异常", err_obj=e)
            return None, "信息表扩展信息新增或者修改异常:" + str(e)

    @staticmethod
    def get_extend_info(thread_id_list: list = None):
        """
        获取映射后的扩展数据
        :param thread_id_list: 信息ID列表
        :return: extend_list, err
        """
        # 参数类型校验
        thread_id_list, is_void = force_transform_type(variable=thread_id_list, var_type="list")
        if not thread_id_list:
            return [], None

        # 信息与类别映射
        thread_category_list = list(Thread.objects.filter(id__in=thread_id_list).values("id", "category_id"))
        thread_category_map = {i["id"]: i["category_id"] for i in thread_category_list if i.get("category_id", None)}

        # 扩展字段映射, 如没有配置对应类别的扩展字段，则无法添加扩展数据。
        extend_fields = list(ThreadExtendField.objects.values("category_id", "field_index", "field"))
        if not extend_fields:
            return [], None
        extend_field_map = {}
        for item in extend_fields:
            if extend_field_map.get(item["category_id"]):
                extend_field_map[item["category_id"]].update({item["field_index"]: item["field"]})
            else:
                extend_field_map[item["category_id"]] = {item["field_index"]: item["field"],
                                                         "thread_id_id": "thread_id"}

        # 查询出扩展原始数据
        try:
            thread_extend_list = list(ThreadExtendData.objects.filter(thread_id__in=thread_id_list).values())
        except Exception as e:
            return [], "获取扩展数据异常"

        # 处理获取到结果，字段替换
        try:
            finish_list = []
            for i in thread_extend_list:
                # 查看该条信息是否指定category_id，眉头则跳过
                current_category_id = thread_category_map.get(i["thread_id_id"], None)
                if not current_category_id:
                    continue
                # 如果该类别没有配置扩展字段则跳过
                current_extend_fields = extend_field_map.get(current_category_id, {})
                if not current_extend_fields:
                    continue
                # 进行替换
                finish_list.append(format_params_handle(
                    param_dict=i,
                    alias_dict=current_extend_fields,
                    is_remove_null=False
                ))
            # 剔除不需要的字段
            finish_list = filter_result_field(
                result_list=finish_list,
                remove_filed_list=[i.name for i in ThreadExtendData._meta.fields if not i.name == "thread_id"]
            )
            return finish_list, None
        except Exception as e:
            write_to_log(prefix="获取映射后的扩展数据,数据拼接异常", err_obj=e,
                         content="thread_id_list:" + str(thread_id_list))
            return [], None


# 主表扩展字段增删改查
class ThreadMainExtendService:
    int_extend_fields = ["field_1", "field_2", "field_3", "field_4", "field_5"]
    char_extend_fields = ["field_6", "field_7", "field_8", "field_9", "field_10", "field_11", "field_12", "field_13",
                          "field_14", "field_15"]
    # 扩展类型
    extend_types = ['str', 'int', 'bool', 'float', 'dict', 'list', 'date']
    all_main_extend_fields = int_extend_fields + char_extend_fields
    extend_fields = []

    def __init__(self, category_id):
        # 获取扩展字段
        category_id, err = force_transform_type(variable=category_id, var_type="int")
        if not category_id:
            self.extend_fields = []
            # self.extend_fields = list(ThreadMainExtendField.objects.all().values(
            #     "id", "category_id", "field", "field_index", "value", "type", "unit", "config", "default"
            # ))
        else:
            self.extend_fields = list(ThreadMainExtendField.objects.filter(category_id=category_id).values(
                "id", "category_id", "field", "field_index", "value", "type", "unit", "config", "default"
            ))

    def format_params_beforehand(self):
        """
        数据过滤预先处理
        :return:(filter_filed_list,alias_dict), err_info
        """
        # 获取过滤字段以及映射字典
        alias_dict = {}
        filter_filed_list = []
        for i in self.extend_fields:
            if not i["field_index"] in ThreadMainExtendService.all_main_extend_fields:
                continue
            filter_filed_key = i["field"] + (f'|{i["type"]}' if i["type"] and i["type"] in self.extend_types else
                                             "|float" if i["field_index"] in ThreadMainExtendService.int_extend_fields
                                             else "|str")
            filter_filed_list.append(filter_filed_key)
            alias_dict[i["field"]] = i["field_index"]
        return (filter_filed_list, alias_dict), None

    def validate(self, params: dict):
        """
        验证长度验证，默认值处理
        :return: params
        """
        params, err = force_transform_type(variable=params, var_type="only_dict", default={})
        if err:
            return params, err

        field_map = {i["field_index"]: i for i in self.extend_fields if
                     i["field_index"] in ThreadMainExtendService.all_main_extend_fields}
        for field_index, map in field_map.items():
            # 判断字符串字段是否超出长度
            if params.get(field_index) and field_index in self.char_extend_fields and len(
                    params.get(field_index)) > 255:
                return None, (map.get("field") + " 长度不可以超过255个字符串")

            # 如果该字段为空或者未传，又配置了扩展字段德默认值，则字段进行赋值
            elif (not params.get(field_index) and map.get("default")):
                params[field_index] = map.get("default")

        return params, None

    @staticmethod
    def replace_list_extend(result_list: list):
        """
        转换主表的扩展字段
        :param result_list: 列表字典
        :return: data,err
        """
        try:
            main_extend_list = list(ThreadMainExtendField.objects.all().values(
                "id", "category_id", "field", "field_index", "value", "type", "unit", "config", "default"
            ))
            main_extend_category_map = {}
            for i in main_extend_list:
                if not main_extend_category_map.get(i["category_id"]):
                    main_extend_category_map[i["category_id"]] = {i["field_index"]: i["field"]}
                else:
                    main_extend_category_map[i["category_id"]][i["field_index"]] = i["field"]

            new_result_list = []
            for result in result_list:
                result = format_params_handle(
                    param_dict=result,
                    is_remove_null=False,
                    alias_dict=main_extend_category_map.get(result["category_id"], {})
                )
                result = format_params_handle(
                    param_dict=result,
                    is_remove_null=False,
                    remove_filed_list=ThreadMainExtendService.all_main_extend_fields
                )
                new_result_list.append(result)
            return new_result_list, None

        except Exception as e:
            return result_list, str(e)
