# encoding: utf-8
"""
@project: djangoModel->thread_tags
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 信息标签下相关接口
@created_time: 2023/4/16 12:36
"""
from rest_framework.decorators import api_view
from rest_framework.views import APIView

from ..services.thread_tag_service import ThreadTagService, ThreadTagMappingService
from ..utils.custom_response import util_response
from ..utils.custom_tool import request_params_wrapper
from ..utils.user_wrapper import user_authentication_wrapper, user_authentication_force_wrapper


class ThreadTagAPIView(APIView):

    @api_view(["GET"])
    @request_params_wrapper
    @user_authentication_wrapper
    def tag_list(self, *args, request_params=None, user_info=None, **kwargs):
        if user_info is None:
            user_info = {}
        if request_params is None:
            request_params = {}

        # 获取当前用户信息
        request_params["user_id"] = user_info.get("user_id")

        # 查询列表
        data, err = ThreadTagService.tag_list(params=request_params)
        if err:
            return util_response(err=1000, msg=err)
        return util_response(data=data)

    @api_view(["POST", "PUT"])
    @request_params_wrapper
    @user_authentication_force_wrapper
    def add_tag(self, *args, request_params=None, user_info=None, **kwargs):
        if user_info is None:
            user_info = {}
        if request_params is None:
            request_params = {}

        # 获取当前用户信息
        request_params['user_id'] = user_info.get("user_id")
        data, err = ThreadTagService.add_tag(add_params=request_params)
        if err:
            return util_response(err=1000, msg=err)
        return util_response(data=data)

    @api_view(["POST", "DELETE"])
    @request_params_wrapper
    @user_authentication_force_wrapper
    def del_tag(self, *args, request_params=None, user_info=None, **kwargs):
        if user_info is None:
            user_info = {}
        if request_params is None:
            request_params = {}

        # 获取当前用户信息
        user_id = user_info.get("user_id")
        del_pk = request_params.get("pk") or request_params.get("id") or kwargs.get("pk")
        data, err = ThreadTagService.del_tag(del_pk=del_pk, user_id=user_id)
        if err:
            return util_response(err=1000, msg=err)
        return util_response(data=data)

    @api_view(["GET"])
    @request_params_wrapper
    @user_authentication_wrapper
    def get_top_tags(self, *args, request_params=None, user_info=None, **kwargs):
        if user_info is None:
            user_info = {}
        if request_params is None:
            request_params = {}
        # 获取当前用户信息

        data, err = ThreadTagService.get_top_tags()
        if err:
            return util_response(err=1000, msg=err)
        return util_response(data=data)

    @api_view(["POST", "PUT"])
    @request_params_wrapper
    @user_authentication_force_wrapper
    def add_tag_map(self, *args, request_params=None, **kwargs):
        if request_params is None:
            request_params = {}
        thread_id = request_params.get("thread_id")
        tag_id = request_params.get("tag_id")

        data, err = ThreadTagMappingService.add_tag_map(thread_id=thread_id, tag_id=tag_id)
        if err:
            return util_response(err=1000, msg=err)
        return util_response(data=data)

    @api_view(["POST", "DELETE"])
    @request_params_wrapper
    @user_authentication_force_wrapper
    def del_tag_map(self, *args, request_params=None, **kwargs):
        if request_params is None:
            request_params = {}
        thread_id = request_params.get("thread_id")
        tag_id = request_params.get("tag_id")

        data, err = ThreadTagMappingService.del_tag_map(thread_id=thread_id, tag_id=tag_id)
        if err:
            return util_response(err=1000, msg=err)
        return util_response(data=data)

    @api_view(["GET"])
    @request_params_wrapper
    @user_authentication_force_wrapper
    def tag_thread(self, *args, request_params=None, **kwargs):
        if request_params is None:
            request_params = {}

        data, err = ThreadTagMappingService.tag_thread(params=request_params)
        if err:
            return util_response(err=1000, msg=err)
        return util_response(data=data)
