"""
Created on 2022-04-11
@author:刘飞
@description:发布子模块逻辑处理
"""
import logging

from django.db.models import F, Q

from xj_user.services.user_platform_service import UserPlatformService
from ..models import ThreadCategory, ThreadClassify
from ..utils.custom_tool import force_transform_type
from ..utils.j_recur import JRecur

log = logging.getLogger()


class ThreadCategoryTreeServices:
    def __init__(self):
        pass

    @staticmethod
    def get_category_tree(category_id: int = None, category_value: str = None):
        """
        类别树。
        注意：该方法支持category_id与category_value搜索。不传则查询全部。
        :param category_id: 类别ID。
        :param category_value: 类别Value。注意：
        :return: category_tree，err
        """
        # 第一步，把类别列表全部读出来
        category_set = ThreadCategory.objects.filter(Q(is_deleted__isnull=True) | Q(is_deleted=0)).annotate(category_value=F('value')).order_by('sort')
        category_set = category_set.values(
            'id',
            'platform_code',
            'category_value',
            'name',
            'need_auth',
            'description',
            'sort',
            'parent_id',
        )
        category_list = list(category_set)

        # 第二步，遍历列表，把数据存放在dict里
        category_id, is_pass = force_transform_type(variable=category_id, var_type="int")
        filter_key = 'id' if category_id else ('category_value' if category_value else None)
        filter_value = category_id if category_id else (category_value if category_value else None)

        # 第三步，把所有的数据创建成树
        category_tree = JRecur.create_forest(source_list=category_list)

        # 第四步，查找任意节点下面的数据
        if filter_key and filter_value:
            category_tree = JRecur.filter_forest(category_tree, filter_key, filter_value)
            if len(category_tree) == 1:
                category_tree = category_tree[0]

        return category_tree, None

    @staticmethod
    def get_category_tree_by_user(user_id: int = None):
        """
        获取这个平台下面的所有分类（结构：类别树）。
        :param user_id: 用户ID
        :return: category_tree, err
        """
        # 第一步，把类别列表全部读出来
        user_id, is_pass = force_transform_type(variable=user_id, var_type="int")
        if not user_id:
            return None, "不是一个有效的用户"
        platform_info, err = UserPlatformService.get_platform_info_by_user_id(user_id)
        if err:
            return None, err
        platform_code_list = [i["platform_code"] for i in platform_info]

        category_set = ThreadCategory.objects.filter(
            is_deleted=0,
            platform_code__in=platform_code_list
        ).annotate(category_value=F('value')).order_by('sort').values(
            'id',
            'platform_code',
            'category_value',
            'name',
            'need_auth',
            'description',
            'sort',
            'parent_id',
        )
        category_list = list(category_set)
        # 第二步，遍历列表，把数据存放在dict里
        category_tree = JRecur.create_forest(source_list=category_list)
        # category_tree = JRecur.filter_forest(category_tree, 'platform_code', platform_info.get("platform_code"))
        category_tree = category_tree[0] if len(category_tree) == 1 else category_tree
        return category_tree, None

    @staticmethod
    def get_child_ids(category_id=None, category_value=None):
        """
        获取该类别下面所有类别ID，
        :param category_id: 类别ID
        :param category_value: 分类value
        :return: out_list, err
        """
        category_id, is_pass = force_transform_type(variable=category_id, var_type="int")
        if not category_id and not category_value:
            return None, "参数错误"
        category_set = ThreadCategory.objects.filter(is_deleted=0).annotate(category_value=F('value'))
        category_set = category_set.filter(id=category_id) if category_id else category_set.filter(category_value=category_value)
        if not category_set.first():
            return None, "没有找到该类别信息"
        current_category = category_set.values('id', 'parent_id').first()

        category_tree = JRecur.create_forest(source_list=list(ThreadCategory.objects.filter(is_deleted=0).values('id', 'parent_id')))
        filter_category_tree = JRecur.filter_forest(category_tree, "id", current_category["id"])
        out_list = JRecur.filter_tree_values(filter_category_tree, "id", )
        return out_list, None

    @staticmethod
    def get_category_classify_tree(params=None):
        """
        类别树。
        注意：该方法支持category_id与category_value搜索。不传则查询全部。
        :param params: 搜索参数
        :return: category_tree，err
        """
        params, err = force_transform_type(variable=params, var_type="only_dict", default={})
        # 查询参数过滤，替换

        # 第一步，把类别列表全部读出来
        category_set = ThreadCategory.objects.annotate(category_value=F('value')).filter(is_deleted=0).order_by('sort')
        category_list = list(category_set.values(
            'id',
            'platform_code',
            'category_value',
            'name',
            'need_auth',
            'description',
            'sort',
            'parent_id',
        ))
        for i in category_list:
            i["parent_id"] = '0' if i["parent_id"] is None else i["parent_id"]

        # 第二步，把所有的数据创建成树
        category_tree = JRecur.create_forest(source_list=category_list)

        # 第三步、过滤类别数
        if params:
            for k, v in params.items():
                category_tree = JRecur.filter_forest(
                    source_forest=category_tree,
                    find_key=k,
                    find_value=v,
                )

        # 第四步，获取分类并简历映射
        classify_set_list = list(ThreadClassify.objects.annotate(classify_value=F('value')).order_by('sort').values(
            "id",
            "name",
            "show",
            "classify_value",
            "category_id",
            "description",
            "icon",
            "sort",
            "parent",
            "config",
        ))
        classify_set_map = {}
        for classify_set in classify_set_list:
            index = str(classify_set['category_id'])
            if index not in classify_set_map.keys():
                classify_set_map[index] = []
            classify_set_map[index].append(classify_set)

        # 第五步，统一名称字段，数据拼接
        def parse_tree(tree, category_id=None):
            for item in tree:
                if "children" not in item.keys():
                    item['children'] = []
                if len(item['children']) > 0:
                    parse_tree(item['children'], item["id"])

                if str(item['id']) in classify_set_map.keys():
                    classify_list = classify_set_map[str(item['id'])]
                    for i in classify_list:
                        i["type"] = "classify"
                    item['children'].extend(classify_set_map[str(item['id'])])
                item["type"] = "category"
            return tree

        return parse_tree(category_tree, 0), None
