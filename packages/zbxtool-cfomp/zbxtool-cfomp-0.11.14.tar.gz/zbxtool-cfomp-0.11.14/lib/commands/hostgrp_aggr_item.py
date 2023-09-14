#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Gary
# Datetime: 2022/12/19 14:33
# IDE: PyCharm
"""
    在 "Zabbix server" 主机上创建各主机组的内存、磁盘、CPU 使用情况的聚合（计算）型监控项：
        1. 如果不存在此监控项则立即创建，如果标签不存在也会自动创建：
            1.1 内存聚合监控项默认添加到 "Memory aggregation" 标签；
            1.1 磁盘聚合监控项默认添加到 "Filesystem aggregation" 标签；
            1.1 CPU聚合监控项默认添加到 "CPU aggregation" 标签；
        2. 如果已存在此监控项则更新监控项或者不做操作。
"""
import argparse
import logging
from lib.utils.zbxapis import ZabbixApiCreate, ZabbixApiUpdate
from lib.utils.format import md5_, get_value, DiskCache
from lib.utils.zbxtags import ItemTags


class Items:
    def __init__(self, zapi):
        self._zapi = zapi
        self._name = "Zabbix server"
        self._cache = DiskCache()

    @property
    def server_hostid(self):
        if self._cache.get_cache("hostid_zbx_server"):
            return self._cache.get_cache("hostid_zbx_server")
        if not self._cache.get_cache("hostid_zbx_server"):
            server_host = ZabbixApiCreate(self._zapi).get_hts(
                filter_={"host": "Zabbix server"}
            )
            if server_host:
                self._cache.set_cache(
                    "hostid_zbx_server",
                    server_host[0].get("hostid"),
                    expire=300
                )
                return self._cache.get_cache("hostid_zbx_server")

    def get_item_info(self, name: str):
        item = ZabbixApiCreate(self._zapi).get_items(
            hostids=[self.server_hostid],
            filter_={"name": name},
            output=["itemid", "params"],
            selecthosts=["host", "status", "tags"],
            selecttags="extend"
        )
        if item and item[0].get("itemid") and item[0].get("params"):
            return item[0].get("itemid"), item[0].get("params"), \
                   item[0].get("tags"), item[0].get("hosts")[0].get("host")

    def update(self, name: str, params: str, tag_name: str):
        if self.get_item_info(name):
            itemid = self.get_item_info(name)[0]
            item_tags = ItemTags(self.get_item_info(name)[2]).added_item_tags(
                tag_name="Application",
                tag_value=tag_name
            )
            if itemid and self.get_item_info(name)[1]:
                if self.get_item_info(name)[1] != params or \
                        self.get_item_info(name)[2] != item_tags:
                    ZabbixApiUpdate(self._zapi).update_item(
                        {
                            "itemid": itemid,
                            "params": params,
                            "tags": item_tags
                        }
                    )
                    logging.info(
                        "\033[32m主机 '%s' 成功更新监控项: '(ItemID)%s' => '(ItemName)%s'\033[0m",
                        self.get_item_info(name)[3],
                        itemid,
                        name
                    )
                else:
                    logging.info(
                        "\033[33m主机 '%s' 监控项未发生改变：'(ItemID)%s' => '(ItemName)%s'\033[0m",
                        self.get_item_info(name)[3],
                        itemid,
                        name
                    )

    def create(self, item_name=None, delay=None, key_=None, tag_value=None,
               type_=15, value_type=3, data_type=0, units="B", params=None):
        """
            创建 Zabbix Item：
                1. Zabbix 6.0 版本 item 类型没有 "Zabbix aggregate" 了；
                2. 以往的 "Zabbix aggregate" 需使用 "calculated" 来代替；
                3. 创建一个 "calculated" 类型的 item，主要包含三部分：item name、item key、formula；
                4. Zabbix 6.0 中的 "formula" 语法与以往稍有不同，
                   例如：sum(last_foreach(/*/vfs.fs.usedsize?[group="%s"]))。
        :param tag_value:
        :param item_name:
        :param delay:
        :param key_:
        :param type_:
        :param value_type:
        :param data_type:
        :param units:
        :param params:
        :return:
        """
        if not self.get_item_info(item_name):
            ZabbixApiCreate(self._zapi).create_item(
                delay=delay,
                hostid=self.server_hostid,
                key_=key_,
                name=item_name,
                type=type_,
                value_type=value_type,
                data_type=data_type,
                units=units,
                params=params,
                tags=[{"tag": "Application", "value": tag_value}]
            )
            logging.info(
                "\033[32m主机 '%s' 成功创建监控项 '%s'\033[0m",
                self.get_item_info(item_name)[3],
                item_name
            )

    def create_total_disk_space_item(self, grp: str):
        """
            创建主机组【总磁盘空间】监控项：
        :param grp:
        :return:
        """
        item_name = get_value(
            section="ZABBIX",
            option="TOTAL_DISK_SPACE_ITEM_NAME",
            raw=True
        ) % grp
        params = get_value(
            section="ZABBIX",
            option="TOTAL_FS_SIZE_PARAMS",
            raw=True
        ) % grp
        self.update(name=item_name, params=params, tag_name="Filesystem aggregation")
        self.create(
            item_name=item_name,
            key_=get_value(
                section="ZABBIX",
                option="TOTAL_FS_SIZE_ITEM",
                raw=True
            ) % grp,
            delay=3600,
            params=params,
            tag_value="Filesystem aggregation"
        )

    def create_used_disk_space_item(self, grp: str):
        """
            创建主机组【已使用磁盘空间】监控项：
        :param grp:
        :return:
        """
        item_name = get_value(
            section="ZABBIX",
            option="USED_DISK_SPACE_ITEM_NAME",
            raw=True
        ) % grp
        params = get_value(
            section="ZABBIX",
            option="USED_FS_SIZE_PARAMS",
            raw=True
        ) % grp
        self.update(name=item_name, params=params, tag_name="Filesystem aggregation")
        self.create(
            item_name=item_name,
            key_=get_value(
                section="ZABBIX",
                option="USED_FS_SIZE_ITEM",
                raw=True
            ) % grp,
            delay=3600,
            params=params,
            tag_value="Filesystem aggregation"
        )

    def create_used_disk_space_per_item(self, grp: str):
        """
            创建主机组【磁盘空间使用率】监控项：
        :param grp:
        :return:
        """
        item_name = get_value(
            section="ZABBIX",
            option="USED_DISK_SPACE_PERCENTAGE_ITEM_NAME",
            raw=True
        ) % grp
        params = get_value(
            section="ZABBIX",
            option="DISK_SPACE_PARAMS",
            raw=True
        ) % (self._name, grp, self._name, grp)
        self.update(name=item_name, params=params, tag_name="Filesystem aggregation")
        self.create(
            item_name,
            key_=md5_(
                get_value(
                    section="ZABBIX",
                    option="USED_DISK_SPACE_PERCENTAGE_ITEM",
                    raw=True
                ) % grp),
            delay=86400,
            value_type=0,
            units="%",
            params=params,
            tag_value="Filesystem aggregation"
        )

    def create_total_vm_item(self, grp: str):
        """
            创建主机组【总内存空间】监控项：
        :param grp:
        :return:
        """
        item_name = get_value(
            section="ZABBIX",
            option="TOTAL_VM_SIZE_ITEM_NAME",
            raw=True
        ) % grp
        params = get_value(
            section="ZABBIX",
            option="TOTAL_VM_SIZE_PARAMS",
            raw=True
        ) % grp
        self.update(name=item_name, params=params, tag_name="Memory aggregation")
        self.create(
            item_name=item_name,
            key_=get_value(
                section="ZABBIX",
                option="TOTAL_VM_SIZE_ITEM",
                raw=True
            ) % grp,
            delay=600,
            params=params,
            tag_value="Memory aggregation"
        )

    def create_used_vm_item(self, grp: str):
        """
            创建主机组【已使用内存】监控项：
        :param grp:
        :return:
        """
        item_name = get_value(
            section="ZABBIX",
            option="USED_VM_SIZE_ITEM_NAME",
            raw=True
        ) % grp
        params = get_value(
            section="ZABBIX",
            option="USED_VM_SIZE_PARAMS",
            raw=True
        ) % grp
        self.update(name=item_name, params=params, tag_name="Memory aggregation")
        self.create(
            item_name=item_name,
            key_=get_value(
                section="ZABBIX",
                option="USED_VM_SIZE_ITEM",
                raw=True
            ) % grp,
            delay=600,
            params=params,
            tag_value="Memory aggregation"
        )

    def create_used_vm_per_item(self, grp: str):
        """
            创建主机组【内存使用率】监控项：
        :param grp:
        :return:
        """
        item_name = get_value(
            section="ZABBIX",
            option="VM_UTIL_ITEM_NAME",
            raw=True
        ) % grp
        params = get_value(
            section="ZABBIX",
            option="VM_SPACE_PARAMS",
            raw=True
        ) % (self._name, grp, self._name, grp)
        self.update(name=item_name, params=params, tag_name="Memory aggregation")
        self.create(
            item_name=item_name,
            key_=md5_(
                get_value(
                    section="ZABBIX",
                    option="USED_VM_SPACE_PERCENTAGE_ITEM",
                    raw=True
                ) % grp
            ),
            delay=3600,
            value_type=0,
            units="%",
            params=params,
            tag_value="Memory aggregation"
        )

    def create_avg_cpu_item(self, grp: str):
        """
            创建主机组【CPU平均使用率】监控项：
        :param grp:
        :return:
        """
        item_name = get_value(
            section="ZABBIX",
            option="AVG_CPU_UTIL_ITEM_NAME",
            raw=True
        ) % grp
        params = get_value(
            section="ZABBIX",
            option="CPU_UTIL_PARAMS",
            raw=True
        ) % grp
        self.update(name=item_name, params=params, tag_name="CPU aggregation")
        self.create(
            item_name=item_name,
            key_=get_value(
                section="ZABBIX",
                option="CPU_UTIL_ITEM",
                raw=True
            ) % grp,
            delay=60,
            value_type=0,
            units="%",
            params=params,
            tag_value="CPU aggregation"
        )


def main(args):
    """main function"""
    instance_ = Items(args.zapi)
    for grp in args.hostgroup:
        instance_.create_total_disk_space_item(grp)
        instance_.create_used_disk_space_item(grp)
        instance_.create_used_disk_space_per_item(grp)
        instance_.create_total_vm_item(grp)
        instance_.create_used_vm_item(grp)
        instance_.create_used_vm_per_item(grp)
        instance_.create_avg_cpu_item(grp)


parser = argparse.ArgumentParser()
parser.add_argument("hostgroup", nargs="+", help="host group name")
parser.set_defaults(handler=main)
