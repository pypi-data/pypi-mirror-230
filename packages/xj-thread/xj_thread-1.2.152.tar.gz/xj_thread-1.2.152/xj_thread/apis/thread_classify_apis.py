# encoding: utf-8
"""
@project: djangoModel->thread_category_apis
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 类别api
@created_time: 2022/10/25 14:40
"""
from rest_framework.views import APIView

from ..services.thread_classify_service import ThreadClassifyService
from ..utils.custom_response import util_response
from ..utils.custom_tool import request_params_wrapper


class ThreadClassifyApis(APIView):
    @request_params_wrapper
    def add(self, *args, request_params=None, **kwargs):
        data, err = ThreadClassifyService.add(request_params)
        if err:
            return util_response(err=1000, msg=err)
        return util_response(data=data)

    @request_params_wrapper
    def delete(self, *args, request_params=None, **kwargs):
        pk = kwargs.get("pk") or request_params.get("id") or request_params.get("category_id")
        data, err = ThreadClassifyService.delete(pk)
        if err:
            return util_response(err=1000, msg=err)
        return util_response(data=data)

    @request_params_wrapper
    def edit(self, *args, request_params=None, **kwargs):
        pk = kwargs.get("pk") or request_params.get("id") or request_params.get("category_id")
        data, err = ThreadClassifyService.edit(request_params, pk)
        if err:
            return util_response(err=1000, msg=err)
        return util_response(data=data)

    @request_params_wrapper
    def list(self, *args, request_params=None, **kwargs):
        if request_params is None:
            request_params = {}
        need_pagination = request_params.pop("need_pagination", None)
        filter_fields = request_params.pop("filter_fields", None)
        need_category_child = request_params.pop("need_category_child", None)
        request_params.setdefault("classify_value", kwargs.get("classify_value", None))
        data, err = ThreadClassifyService.list(
            params=request_params,
            need_pagination=need_pagination,
            filter_fields=filter_fields,
            need_category_child=need_category_child
        )
        if err:
            return util_response(err=1000, msg=err)
        return util_response(data=data)
