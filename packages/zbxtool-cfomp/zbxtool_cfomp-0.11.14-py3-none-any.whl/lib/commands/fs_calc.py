#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Gary
# Datetime: 2022/12/19 18:57
# IDE: PyCharm
"""
    在 Zabbix 主机上创建 vfs.fs.totalsize 和 vfs.fs.usedsize 这两个【计算型】监控项：
        1. 如果不存在此监控项则立即创建，并且默认添加到 "Application: Disk calculated" 标签，
           如果标签不存在也会自动创建；
        2. 如果已存在此监控项则更新监控项或者不做操作。
"""
import argparse
import logging
from lib.utils.zbxapis import ZabbixApiUpdate, ZabbixApiCreate
from lib.utils.format import get_value
from lib.utils.zbxtags import ItemTags


class ZbxCalculatedItems:
    def __init__(self, zapi):
        self._zapi = zapi

    def get_fs_size_items(self, hostid: str):
        """
            获取带有 "vfs.fs.size" 关键字的全部监控项：
                1. 监控项主要分为 "used"、"pused"、"total" 三类；
        :param hostid:
        :return:
        """
        return self._zapi.get_items(
            hostids=[hostid],
            search={
                "key_": get_value(
                    section="ZABBIX",
                    option="FS_SIZE_ITEM_KEY"
                )
            },
            selectinterfaces=["ip"],
            selecthosts=["host", "status", "tags"],
            selecttags="extend"
        )

    @staticmethod
    def gen_formula(mode: str, items: list, extra="pused"):
        """
            生成 "Calculated" 类型的 item 的表达式：
                1. 表达式由三部分构成 func(/IP ADDRESS/ITEM KEY)，即函数、ip 和 item key；
        :param mode:
        :param items:
        :param extra:
        :return:
        """
        formula = "+".join(
            [
                "last(/" + item.get("hosts")[0].get("host") + "/" + item.get("key_") + ")"
                for item in items
                if item.get("hosts")
                if mode in item.get("key_") and extra not in item.get("key_")
            ]
        )
        return formula if formula else "0"


def update_calculated_item(api, get_items: list, mode: str, fs_size_items: list):
    """
        如果已经存在 "Calculated" 类型的 item 则更新它：
            1. 因为重复添加已经存在的 item 会报错，所以当 item 已经存在时则更新它或者不做操作；
    :param api:
    :param get_items:
    :param mode:
    :param fs_size_items:
    :return:
    """
    instance_ = ZbxCalculatedItems(api)
    for item in get_items:
        item_tags = ItemTags(item.get("tags")).added_item_tags(
            tag_name="Application",
            tag_value="Disk calculated"
        )
        if item.get("params") != instance_.gen_formula(mode, fs_size_items) or \
                item.get("tags") != item_tags:
            api.update_item(
                {
                    "itemid": item.get("itemid"),
                    "params": instance_.gen_formula(mode, fs_size_items),
                    "tags": ItemTags(item.get("tags")).added_tags(
                        tag_name="Application",
                        tag_value="Disk calculated"
                    )
                }
            )
            logging.info(
                "\033[32m主机 '%s' 成功更新监控项: '(ItemID)%s' => '(ItemName)%s'\033[0m",
                item.get("hosts")[0].get("host"),
                item.get("itemid"),
                item.get("name")
            )
        else:
            logging.info(
                "\033[33m主机 '%s' 监控项未发生改变：'(ItemID)%s' => '(ItemName)%s'\033[0m",
                item.get("hosts")[0].get("host"),
                item.get("itemid"),
                item.get("name")
            )


def create_calculated_item(api, host: dict, item_name: str,
                           item_key: str, mode: str):
    """
        创建 "Calculated" 类型的 item：
            1. Zabbix 没有直接获取总磁盘和已用磁盘空间的监控项，只有各挂载的文件系统的空间使用情况的监控项；
            2. 因此在各挂载文件系统监控项的基础上创建一个汇总的 Calculated 监控项；
            3. 涉及的监控项为 vfs.fs.size[fs,total] 和 vfs.fs.size[fs,used]；
            4. 创建的计算监控项 key 为 vfs.fs.totalsize 和 vfs.fs.usedsize。
    :param api:
    :param host:
    :param item_name:
    :param item_key:
    :param mode:
    :return:
    """
    instance_ = ZbxCalculatedItems(api)
    result = api.create_item(
        delay=3600,
        hostid=host.get("hostid"),
        key_=item_key,
        name=item_name,
        type_=15,
        value_type=3,
        data_type=0,
        units="B",
        params=instance_.gen_formula(
            mode,
            instance_.get_fs_size_items(host.get("hostid"))
        ),
        tags=[{"tag": "Application", "value": "Disk calculated"}]
    )
    logging.info(
        "\033[32m主机 '%s' 成功创建监控项 '%s'\033[0m",
        host.get("name"),
        item_name
    )
    return result


def calculated_disk(api):
    """
        执行更新/创建 "Calculated" 类型 item 的操作：
    :return:
    """
    instance_ = ZbxCalculatedItems(ZabbixApiUpdate(api))
    hosts = ZabbixApiUpdate(api).get_hts(
        output=["hostid", "name"],
        filter_={"available": 1, "status": 0},
        searchinventory={"os_short": ["Linux", "Windows"]},
        searchbyany=True
    )
    for host in hosts:
        fs_size_items = instance_.get_fs_size_items(host.get("hostid"))
        total_disk_items = ZabbixApiUpdate(api).get_items(
            hostids=host.get("hostid"),
            filter_={"name": get_value(section="ZABBIX", option="TOTAL_ITEM_NAME")},
            selecthosts=["host", "status", "tags"],
            selecttags="extend"
        )
        if len(total_disk_items) == 0:
            create_calculated_item(
                host=host,
                item_name=get_value(section="ZABBIX", option="TOTAL_ITEM_NAME"),
                item_key=get_value(section="ZABBIX", option="TOTAL_ITEM_KEY"),
                mode="total",
                api=ZabbixApiCreate(api)
            )
        else:
            update_calculated_item(
                get_items=total_disk_items,
                mode="total",
                fs_size_items=fs_size_items,
                api=ZabbixApiUpdate(api)
            )
        used_disk_items = ZabbixApiUpdate(api).get_items(
            hostids=host.get("hostid"),
            filter_={"name": get_value(section="ZABBIX", option="USED_ITEM_NAME")},
            selecthosts=["host", "status", "tags"],
            selecttags="extend"
        )
        if len(used_disk_items) == 0:
            create_calculated_item(
                host=host,
                item_name=get_value(section="ZABBIX", option="USED_ITEM_NAME"),
                item_key=get_value(section="ZABBIX", option="USED_ITEM_KEY"),
                mode="used",
                api=ZabbixApiCreate(api)
            )
        else:
            update_calculated_item(
                get_items=used_disk_items,
                mode="used",
                fs_size_items=fs_size_items,
                api=ZabbixApiUpdate(api)
            )


def main(args):
    """
        在各主机上创建总磁盘空间和已用磁盘空间两个监控项：
    :param args:
    :return:
    """
    calculated_disk(api=args.zapi)


parser = argparse.ArgumentParser()
parser.set_defaults(handler=main)
