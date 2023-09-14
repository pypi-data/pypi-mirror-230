#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Gary
# Datetime: 2022/12/20 13:25
# IDE: PyCharm
import collections
from .format import get_value, jmes_search


def parse_inventory_tag_literal(inventory_tag: str):
    """
        将一连串以英文分号分割的 "k=v" 转化为字典：
    :param inventory_tag:
    :return:
    """
    res = {}
    if inventory_tag is None:
        return res
    if not isinstance(inventory_tag, str):
        raise TypeError()
    tags = inventory_tag.strip().split(";")
    for item in tags:
        item = item.strip()
        pos = item.find("=")
        if pos < 0:
            key = item.rstrip()
            if len(key) > 0:
                res[key] = None
        elif pos > 0:
            key = item[0: pos].rstrip()
            if len(key) > 0:
                res[key] = item[pos + 1:].lstrip()
    return res


class InventoryTagDict(collections.UserDict):
    """
        处理 host inventory 中的 tag 字段：
            1. 由于 Zabbix 3.0/4.0 版本 host 不支持 tag 功能，缓解方法是在 host inventory 的 tag 字段定稿相应的 tag；
            2. inventory tag 的格式规范是以分号分隔的 k=v 或者 k 字符串，如：key1=val1;key2;key3=val3。
    """

    def __init__(self, inventory_tag=None):
        super().__init__(parse_inventory_tag_literal(inventory_tag))

    def __setitem__(self, key, item):
        if not isinstance(item, str) and item is not None:
            raise TypeError()
        super().__setitem__(key, item)

    def __str__(self):
        res = ""
        for k, v in self.data.items():
            res += k
            if v:
                res += ("=" + v)
            res += ";"
        return res


class HostTags:
    """
        处理 Zabbix Host 的 tag:
            1. Zabbix 6.0 版本中 Host 已支持 tag；
            2. 主要涉及到 Host tag 的新增和删除操作。
    """

    def __init__(self, tags: list):
        self._tags = tags

    @property
    def format_tags(self) -> list:
        """
            去除 host tag 字典中 "automatic" key：
                1. 一个 host 的 tag 字典中主要包含三个 key: tag、value、automatic；
                2. 在通过 Zabbix Api 操作 host tag 时，tag 字典中不能包含 "automatic" key，否则会报错。
        :return:
        """
        if self._tags:
            for tag in self._tags:
                if isinstance(tag, dict) and "automatic" in tag.keys():
                    del tag["automatic"]
            return self._tags
        return []

    def have(self, tag_name: str) -> bool:
        """
            判断 host 中是否包含某个 tag：
        :param tag_name: host tag Name
        :return:
        """
        return bool(
            jmes_search(
                jmes_rexp=get_value(
                    section="JMES",
                    option="SEARCH_HOST_TAG",
                    raw=True
                ) % tag_name,
                data=self._tags
            )
        )

    def added_tags(self, tag_name: str, tag_value: str or int or None):
        """
            往 host 中添加 tag 并返回字典列表：
        :param tag_name: host tag Name
        :param tag_value: host tag Value
        :return:
        """
        if not self.have(tag_name):
            self._tags.append(
                {
                    "tag": tag_name,
                    "value": tag_value
                }
            )
            return self.format_tags
        return self.format_tags

    def get_del_tag_value(self, tag_name: str):
        if self._tags:
            for host_tag in self._tags:
                if host_tag.get("tag") and host_tag.get("tag") == tag_name:
                    return host_tag.get("value")

    def deleted_tags(self, tag_name: str):
        """
            从 host 中删除 tag 并返回字典列表：
        :param tag_name: host tag Name
        :return:
        """
        if self.have(tag_name):
            del self._tags[
                self._tags.index(
                    {
                        "tag": tag_name,
                        "value": self.get_del_tag_value(tag_name)
                    }
                )
            ]
            return self.format_tags
        return self.format_tags


class ItemTags(HostTags):
    def __init__(self, tags: list):
        self._tags = tags
        super().__init__(tags)

    def added_item_tags(self, tag_name: str, tag_value: str or int or None):
        """
            为 Item 添加标签：
                1. 在 Zabbix 旧版本中（如 3.0、4.0），添加监控项时可以将监控项加入对应的 Application，
                   但是在 Zabbix 6.0 版本中已经全面舍弃了 Application；
                2. 虽然新版本舍弃了 Application，但是可以给 Item 分配标签，标签名称默认还是 "Application"。
        :param tag_name:
        :param tag_value:
        :return:
        """
        if self.have(tag_name) and tag_name == "Application":
            for tag in self._tags:
                if tag.get("tag") == "Application":
                    tag["value"] = tag_value
            return self._tags
        if not self.have(tag_name):
            return self.added_tags(tag_name=tag_name, tag_value=tag_value)
