# encoding: utf-8
"""
@project: djangoModel->thread_tag_service
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 信息标签服务
@created_time: 2023/4/16 12:39
"""
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Sum, F

from ..models import ThreadTag, ThreadTagMapping
from ..services.thread_extend_service import ThreadExtendOutPutService
from ..utils.custom_tool import format_params_handle
from ..utils.join_list import JoinList


class ThreadTagService():
    """
    信息标签相关服务
    """

    @staticmethod
    def tag_list(params=None, tag_id_list=None, need_pagination=False, look_public=False, **kwargs):
        """
        标签列表
        :param look_public: 是否查看公域标签
        :param tag_id_list: 标签ID列表
        :param params: 查询参数
        :param need_pagination: 是否分页
        :return:  data,err
        """
        # 默认值
        if params is None:
            params = {}
        if tag_id_list is None:
            tag_id_list = []
        params.setdefault("look_public", look_public)

        # 参数过滤,强制类型转换
        params = format_params_handle(
            param_dict=params,
            filter_filed_list=["page|int", "size|int", "user_id|int", "look_public|bool"],
            is_remove_null=True,
            is_remove_empty=False
        )

        # 获取参数
        size = params.pop('size', 50)
        page = params.pop('page', 1)
        user_id = params.get("user_id", 0)  # 未登录的人，只能看公域标签

        # **构建ORM对象**
        thread_tag_obj = ThreadTag.objects.values("id", "value")
        # 如果服务调用直接返回
        if tag_id_list and isinstance(tag_id_list, list):
            try:
                return list(thread_tag_obj.filter(id__in=tag_id_list)), None
            except Exception as e:
                return [], str(e)

        # 登录的用户，希望查看公域标签。
        if params.get("look_public"):
            user_id = 0

        thread_tag_obj = thread_tag_obj.filter(user_id=user_id)

        # 如果数量超过5000个,则进行分页保护则分页返回, 因为后面标签的数量会越来越多。
        total = thread_tag_obj.count()
        is_pagination = need_pagination or total >= 5000
        if is_pagination:
            paginator = Paginator(thread_tag_obj, size)
            try:
                thread_tag_obj = paginator.page(page)
            except PageNotAnInteger:
                thread_tag_obj = paginator.page(1)
            except EmptyPage:
                thread_tag_obj = paginator.page(paginator.num_pages)
            except Exception as e:
                return None, "msg:" + str(e) + ";tip:查询异常"

        # 分情况（is_pagination）返回结果集
        return {
                   'total': total,
                   "page": int(page),
                   "size": int(size),
                   'list': list(thread_tag_obj.object_list)
               } if is_pagination else list(thread_tag_obj), None

    @staticmethod
    def add_tag(add_params=None, **kwargs):
        """
        添加标签
        :param add_params: 添加参数
        :param kwargs: 添加参数
        :return: data,err
        """
        # 加农任内阁流程控制
        if add_params is None:
            add_params = {}
        if kwargs is None:
            kwargs = {}
        add_params.update(kwargs)

        # 参数处理
        params = format_params_handle(
            param_dict=add_params,
            filter_filed_list=["value|str", "user_id|int", "add_public|bool"],
            is_remove_empty=True
        )
        value = params.get("value")
        user_id = params.get("user_id", 0)

        if params.get("add_public"):
            user_id = 0

        # 标签长度校验
        if not value or len(value) >= 50:
            return None, "标签长度不可以超过50"

        # 判断是否存在该标签
        find_tag_obj = ThreadTag.objects.filter(value=value, user_id=user_id).first()
        if find_tag_obj:
            return None, "msg:已存在该标签，无需重新创建"

        # 创建标签
        try:
            ThreadTag.objects.create(value=value, user_id=user_id)
            return None, None
        except Exception as e:
            return None, "添加标签失败：add_tag" + str(e)

    @staticmethod
    def del_tag(del_pk, user_id, is_admin=False, **kwargs):
        """
        删除标签
        :param is_admin: 是否是管理员，用户无法删除公域标签，仅仅可以删除自己的标签。
        :param del_pk: 删除的主键
        :param user_id: 当前用户的user_id
        :return: data, err
        """
        if not user_id or not del_pk:
            return None, "参数错误"

        # 删除标签
        try:
            # 判断该用户是否可以删除该标签
            is_set = ThreadTag.objects.filter(user_id=user_id, id=del_pk).first()
            if not is_set and not is_admin:
                return None, "不可以删除该标签，可能是您的权限不足"

            ThreadTag.objects.filter(id=del_pk).delete()
            return None, None
        except Exception as e:
            return None, "删除标签失败：add_tag" + str(e)

    @staticmethod
    def get_top_tags(top_limit: int = 5, sort_by="views_total", query_pool="public", current_user_id=0):
        """
        获取热力标签
        找到当前 访问或点击或收藏等字段 数量最高的标签
        :param current_user_id: 当前的用户ID
        :param query_pool:  查询池 public|private|all
        :param sort_by: 信息统计因素的数量进行排序，flag_weights, weight, views, plays, comments, likes, favorite, shares
        :param top_limit: 查询前几的标签
        :return:
        """

        # 如果链表查询会在group的时候多加一个value导致效率变慢，所以只拿ID。
        tip_tag_obj = ThreadTagMapping.objects.values("tag_id").annotate(
            weight_total=Sum("statistic__weight"),
            views_total=Sum("statistic__views"),
            plays_total=Sum("statistic__plays"),
            comments_total=Sum("statistic__comments"),
            likes_total=Sum("statistic__likes"),
            favorite_total=Sum("statistic__favorite"),
            shares_total=Sum("statistic__shares"),
        ).order_by("-" + sort_by).values(
            "tag_id",
            "weight_total",
            "views_total",
            "plays_total",
            "comments_total",
            "likes_total",
            "favorite_total",
            "shares_total",
        )

        # 查询公域或者私域标签
        if query_pool == "public":
            tip_tag_obj = tip_tag_obj.filter(tag__user_id=0)
        elif query_pool == "private" and current_user_id:
            tip_tag_obj = tip_tag_obj.filter(tag__user_id=current_user_id)
        else:
            pass

        # 分查查询ID列表
        paginator = Paginator(tip_tag_obj, top_limit)
        try:
            thread_tag_obj = paginator.page(1)
        except EmptyPage:
            thread_tag_obj = paginator.page(paginator.num_pages)
        except Exception as e:
            return None, "msg:" + str(e) + ";tip:查询异常"

        tag_list = list(thread_tag_obj.object_list)
        value_list, err = ThreadTagService.tag_list(tag_id_list=[i["tag_id"] for i in tag_list])
        JoinList(tag_list, value_list, l_key="tag_id", r_key="id").join()
        return tag_list, None


class ThreadTagMappingService():
    @staticmethod
    def add_tag_map(thread_id: int = None, tag_id: int = None):
        # ============ 判断是否可以插入数据 ============
        try:
            thread_id = int(thread_id)
            tag_id = int(tag_id)
            if not thread_id or not tag_id:
                raise TypeError()
        except TypeError:
            return None, "thread_id、tag_id应该是数字类型，且不能为空"

        if not thread_id or not tag_id:
            return None, "参数错误"

        is_set = ThreadTagMapping.objects.filter(thread_id=thread_id, tag_id=tag_id).first()
        if is_set:
            return None, None
        # ============ 判断是否可以插入数据 ============

        ThreadTagMapping.objects.create(
            thread_id=thread_id,
            statistic_id=thread_id,
            tag_id=tag_id
        )
        return None, None

    @staticmethod
    def del_tag_map(thread_id: int = None, tag_id: int = None):
        # ============ 判断是否可以插入数据 ============
        try:
            thread_id = int(thread_id)
            tag_id = int(tag_id)
            if not thread_id or not tag_id:
                raise TypeError()
        except TypeError:
            return None, "thread_id、tag_id应该是数字类型，且不能为空"

        if not thread_id or not tag_id:
            return None, "参数错误"
        try:
            is_set = ThreadTagMapping.objects.filter(thread_id=thread_id, tag_id=tag_id).delete()
        except Exception as del_err:
            return None, "msg:" + str(del_err) + ";tip:删除失败"

        return None, None

    @staticmethod
    def tag_thread(params=None):
        """
        标签查询信息列表
        :param params: 搜索参数
        :return:
        """
        if params is None:
            params = {}

        page = params.pop('page', 1)
        size = params.pop('size', 10)
        sort = params.pop('sort', None)
        sort = sort if sort and sort in ['thread_id', '-thread_id', 'sort', '-sort', 'create_time', '-create_time', 'update_time', '-update_time'] else None
        if int(size) > 100:
            size = 10
        exclude_category_list = params.pop('exclude_category_list').split(',') if params.get('exclude_category_list') else None

        # 允许进行过渡的字段条件
        conditions = format_params_handle(
            param_dict=params,
            filter_filed_list=[
                "category_id|int", "category_name", "category_value", "category_id_list|list", "category_parent_id|int", "platform_code",
                "classify_id|int", "classify_name", "classify_value", "classify_id_list|list", "classify_parent_id|int", "show_value",
                "user_id|int", "user_id_list|list", "thread_id_list|list",
                "title", "create_time_start|date", "create_time_end|date", "access_level", "has_enroll", "has_fee", "has_comment", "need_auth"
            ],
            alias_dict={
                "thread_id_list_list": "thread_id__in",
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
            },
            split_list=["id_list", "category_id_list", "classify_id_list", "user_id_list"],
            is_remove_empty=True,
        )
        # ================== 参数处理 end ==================

        # ==================== 数据检索 start ====================

        thread_map_set = ThreadTagMapping.objects.annotate(
            is_deleted=F("thread__is_deleted"),

            category_value=F("thread__category__value"),
            classify_value=F("thread__classify__value"),
            show_value=F("thread__show__value"),

            category_name=F("thread__category__name"),
            classify_name=F("thread__classify__name"),
            show_name=F("thread__show__name"),
            need_auth=F("thread__category__need_auth"),

            category_id=F("thread__category_id"),
            classify_id=F("thread__classify_id"),
            show_id=F("thread__show_id"),

            user_id=F("thread__user_id"),
            with_user_id=F("thread__with_user_id"),
            title=F("thread__title"),
            subtitle=F("thread__subtitle"),
            content=F("thread__content"),
            summary=F("thread__summary"),
            access_level=F("thread__access_level"),
            author=F("thread__author"),
            ip=F("thread__ip"),
            has_enroll=F("thread__has_enroll"),
            has_fee=F("thread__has_fee"),
            has_comment=F("thread__has_comment"),
            has_location=F("thread__has_location"),
            cover=F("thread__cover"),
            photos=F("thread__photos"),
            video=F("thread__video"),
            files=F("thread__files"),
            price=F("thread__price"),
            is_original=F("thread__is_original"),
            link=F("thread__link"),
            create_time=F("thread__create_time"),
            update_time=F("thread__update_time"),
            logs=F("thread__logs"),
            more=F("thread__more"),
            sort=F("thread__sort"),
            language_code=F("thread__language_code"),
        )
        # 排序
        if sort:
            thread_map_set = thread_map_set.order_by(sort)
        # 指定不需要过滤的类别字段
        if exclude_category_list:
            thread_map_set = thread_map_set.exclude(category_id__in=exclude_category_list)
        # 开始按过滤条件
        try:
            # 注意：为空和0认为是未删除的数据，为1代表删除的
            thread_map_set = thread_map_set.exclude(is_deleted=True).filter(**conditions)
            count = thread_map_set.count()
            thread_set = thread_map_set.values()
        except Exception as e:
            return None, "err:" + e.__str__() + "line:" + str(e.__traceback__.tb_lineno)
        # 分页数据
        finish_set = list(Paginator(thread_set, size).page(page).object_list)
        # ==================== 数据检索 end ====================

        # ================= 扩展数据拼接  start=================
        category_id_list = list(set([item['category_id'] for item in finish_set if item['category_id']]))
        thread_id_list = list(set([item['id'] for item in finish_set if item['id']]))
        extend_merge_service = ThreadExtendOutPutService(category_id_list=category_id_list, thread_id_list=thread_id_list)
        finish_list = extend_merge_service.merge(finish_set)
        # ================= 扩展数据拼接  end  =================

        return {'size': int(size), 'page': int(page), 'total': count, 'list': finish_list}, None
