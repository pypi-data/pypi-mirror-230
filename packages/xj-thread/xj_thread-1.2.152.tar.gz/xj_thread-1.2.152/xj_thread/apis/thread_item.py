"""
Created on 2022-04-11
@description:刘飞
@description:发布子模块单挑数据删除/修改/详情
"""
import sys
from rest_framework.views import APIView
if 'xj_enroll' in sys.modules:
    from xj_enroll.service.enroll_services import EnrollServices
from ..services.thread_item_service import ThreadItemService
from ..utils.custom_response import util_response
from ..utils.custom_tool import request_params_wrapper
from ..utils.user_wrapper import user_authentication_force_wrapper

item_service = ThreadItemService()


class ThreadItemAPI(APIView):
    """单挑信息处理，查，改，删"""

    @request_params_wrapper
    def get(self, *args, request_params, **kwargs):
        """信息表详情"""
        pk = kwargs.get("pk") or request_params.get("pk")
        if not pk:
            return util_response(msg="非法请求", err=1000)
        data, error_text = item_service.detail(pk, filter_fields=request_params.pop("filter_fields", None))
        if not error_text:
            return util_response(data=data)
        return util_response(err=47767, msg=error_text)

    @user_authentication_force_wrapper
    @request_params_wrapper
    def put(self, *args, request_params, **kwargs):
        """信息表编辑"""
        pk = kwargs.get("pk", None)
        if not pk:
            return util_response(msg="非法请求", err=1000)
        data, error_text = item_service.edit(request_params, pk)

        # 报名表同步修改category_id， 不去联动报名的category_id修改
        # TODO 临时注释 20230815 by Sieyoo
        # category_id = request_params.get("category_id", None)
        # if category_id:
        #     data, err = EnrollServices.enroll_edit({"category_id": category_id}, enroll_id=None, search_param={"thread_id": pk})
        #     if err:
        #         write_to_log(prefix="信息修改联动报名状态修改异常：", content="category_id:" + str(category_id) + " thread_id:" + str(pk))

        if not error_text:
            return util_response()
        return util_response(err=1002, msg=error_text)

    @user_authentication_force_wrapper
    def delete(self, *args, **kwargs):
        pk = kwargs.get("pk", None)
        if not pk:
            return util_response(msg="非法请求", err=1000)

        data, error_text = item_service.delete(pk)
        if not error_text:
            return util_response()
        return util_response(err=47767, msg=error_text)
