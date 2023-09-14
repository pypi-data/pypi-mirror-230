"""
Created on 2022-04-11
@description:刘飞
@description:发布子模块逻辑分发
"""

from rest_framework.views import APIView

from ..services.thread_category_tree_service import ThreadCategoryTreeServices
from ..services.thread_list_service import ThreadListService
from ..services.thread_statistic_service import StatisticsService
from ..utils.custom_response import util_response
from ..utils.custom_tool import request_params_wrapper, filter_fields_handler, filter_result_field, dynamic_load_class
from ..utils.join_list import JoinList
from ..utils.user_wrapper import user_authentication_wrapper


class ThreadListAPIView(APIView):
    """
    get: 信息表列表
    post: 信息表新增
    """

    # 我们更希望通过装饰器来做权限验证，这样可以更好的精简API层的代码量 2022.10.3 by Sieyoo
    @user_authentication_wrapper  # 如果有token则返回user_info，无则返回空
    @request_params_wrapper
    def get(self, *args, user_info=None, request_params, **kwargs):
        request_params.setdefault("category_value", kwargs.get("category_value", None))

        # ============== section 是否检查子树的的信息,如果category_id或者category_value都没传则查询全部 start ==============
        need_child = request_params.pop('need_child', None)
        if need_child:
            if not request_params.get("category_id") and not request_params.get("category_value"):
                return util_response(msg="您选择了need_child，无法搜索到对应节点")

            category_ids, category_tree_err = ThreadCategoryTreeServices.get_child_ids(
                category_id=request_params.pop("category_id", None),
                category_value=request_params.pop("category_value", None)
            )
            if category_tree_err:
                return util_response(err=1000, msg="获取类别子节点错误：" + category_tree_err)
            request_params.setdefault("category_id_list", category_ids)
        # ============== section 是否检查子树的的信息,如果category_id或者category_value都没传则查询全部 end ==============
        # 获取列表数据
        thread_serv, error_text = ThreadListService.list(
            params=request_params,
        )
        if error_text:
            return util_response(err=1002, msg=error_text)

        # ======================= section 其他模块信息拼接 合并 start ================================
        thread_id_list = list(set([item['id'] for item in thread_serv['list'] if item['id']]))
        # 统计信息拼接
        statistic_list = StatisticsService.statistic_list(id_list=thread_id_list)
        thread_serv['list'] = JoinList(l_list=thread_serv['list'], r_list=statistic_list, l_key="id",
                                       r_key='thread_id').join()
        # 拼接用户信息
        DetailInfoService, import_err = dynamic_load_class(import_path="xj_user.services.user_detail_info_service",
                                                           class_name="DetailInfoService")
        if not import_err:
            with_user_id_list = list(
                set([item['with_user_id'] for item in thread_serv['list'] if item['with_user_id']]))
            with_user_info_list, err = DetailInfoService.get_list_detail(user_id_list=with_user_id_list,
                                                                         filter_fields=request_params.get(
                                                                             'filter_fields'))  # 请注意 返回协议存在问题
            thread_serv['list'] = JoinList(l_list=thread_serv['list'], r_list=with_user_info_list, l_key="with_user_id",
                                           r_key='user_id').join()

            thread_serv['list'] = filter_result_field(
                result_list=filter_result_field(  # 扩展字段替换
                    result_list=thread_serv['list'],
                    alias_dict={"nickname": "salesman"},
                ),
            )

            user_id_list = list(set([item['user_id'] for item in thread_serv['list'] if item['user_id']]))
            user_info_list, err = DetailInfoService.get_list_detail(user_id_list=user_id_list,
                                                                    filter_fields=request_params.get(
                                                                        'filter_fields'))  # 请注意 返回协议存在问题
            thread_serv['list'] = JoinList(l_list=thread_serv['list'], r_list=user_info_list, l_key="user_id",
                                           r_key='user_id').join()

        UserGroupService, group_import_err = dynamic_load_class(import_path="xj_role.services.user_group_service",
                                                                class_name="UserGroupService")
        if not group_import_err:
            group_id_list = list(set([item['group_id'] for item in thread_serv['list'] if item['group_id']]))
            group_list, group_err = UserGroupService.group_list(
                params={"id_list": group_id_list}
            )
            print(group_list)
            thread_serv['list'] = JoinList(l_list=thread_serv['list'], r_list=group_list['list'], l_key="group_id",
                                           r_key='id').join()

        # 判断是否需要展示定位信息
        LocationService, import_err = dynamic_load_class(import_path="xj_location.services.location_service",
                                                         class_name="LocationService")
        if request_params.get("need_location") and not import_err:
            location_list, err = LocationService.location_list(
                params={"thread_id_list": thread_id_list},
                need_pagination=False,
                filter_fields=[
                    "name", "thread_id", "longitude", "latitude", "altitude", "coordinate_type"
                ]
            )
            if isinstance(location_list, list) and not err:
                thread_serv['list'] = JoinList(l_list=thread_serv['list'], r_list=location_list, l_key="id",
                                               r_key='thread_id').join()
        # ======================= section 其他模块信息拼接 合并 end ================================
        filter_fields = filter_fields_handler(
            default_field_list=[
                "group_name", "id", "category_name", "classify_name", "show_value", "title", "subtitle", "summary",
                "cover", "photos", "video", "author", "avatar", "user_name", "nickname", "region_code",
                "weight", "views", "plays", "comments", "likes", "favorite", "shares", "create_time", "update_time",
                'name', 'altitude', 'coordinate_type', 'longitude', 'created_time', 'region_code', 'latitude',
                'publish_time'
            ],
            input_field_expression=request_params.get('filter_fields', None)
        )
        # 过滤出需要展示的字段
        thread_serv['list'] = filter_result_field(
            result_list=thread_serv['list'],
            filter_filed_list=filter_fields,
        )
        return util_response(data=thread_serv, is_need_parse_json=True)
