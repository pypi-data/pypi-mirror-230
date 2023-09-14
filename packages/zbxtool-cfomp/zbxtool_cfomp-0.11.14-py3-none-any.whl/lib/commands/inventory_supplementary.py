#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Gary
# Datetime: 2022/12/19 19:36
# IDE: PyCharm
"""
    更新 Zabbix 主机的 inventory:
        1. 检索监控项 name 为 "Chassis Model" 的主机，如果最新值包含 "VMware"/"KVM",
           则把主机 inventory type 字段设置为 VM，主机打上 VM 标签；
        2. 检索监控项 key 为 "proc.num[rsync,root,,--daemon]" 的主机：
            1. 如果监控项最新值为 1，则在 host tag 中添加 rsyncd 标签；
            2. 如果监控项最新值为 0，则删除在 host tag 和 host inventory 中的 rsyncd 标签。
"""
import argparse
import logging
from ast import literal_eval
from lib.utils.zbxapis import ZabbixApiUpdate
from lib.utils.format import get_value, jmes_search
from lib.utils.zbxtags import InventoryTagDict, HostTags


class UpdateHtInventory:
    def __init__(self, zapi):
        self.zapi = ZabbixApiUpdate(zapi)

    @staticmethod
    def is_vm(items: list):
        """
            获取 lastvalue 值为 "VMware" 或者 "KVM" 的主机列表：
        :param items:
        :return:
        """
        return list(
            filter(
                lambda item: item.get("lastvalue") in literal_eval(
                    get_value(section="ZABBIX", option="CHASSIS_MODE_TYPES")),
                items
            )
        )

    @staticmethod
    def is_host(items: list):
        return list(
            filter(
                lambda item: item.get("hosts")[0].get("status") != "3",
                items
            )
        )

    @staticmethod
    def inventory(item: dict, host: dict, check_type: str):
        instance_ = HostTags(host.get("tags"))
        inventory_tags = InventoryTagDict(host.get("inventory").get("tag"))
        if check_type == "inventory_type":
            if host.get("hostDiscovery"):
                return {
                    "host_tags": [],
                    "inventory_tags": {"type": "VM"}
                }
            return {
                "host_tags": instance_.added_tags("type", "VM"),
                "inventory_tags": {"type": "VM"}
            }
        if check_type == "inventory_tag":
            # 如果监控项最新值为 1，在 host tag 中添加 rsyncd 标签
            if item["lastclock"] != "0" and item["lastvalue"] == "1":
                if host.get("hostDiscovery"):
                    return {
                        "host_tags": [],
                        "inventory_tags": {"tag": str(inventory_tags)}
                    }
                return {
                    "host_tags": instance_.added_tags("rsyncd", ""),
                    "inventory_tags": {"tag": str(inventory_tags)}
                }
            # 如果监控项最新值为 0，删除 host tag 中的 rsyncd 标签
            if item["lastclock"] != "0" and item["lastvalue"] == "0":
                if "rsyncd" in inventory_tags:
                    del inventory_tags["rsyncd"]
                if host.get("hostDiscovery"):
                    return {
                        "host_tags": [],
                        "inventory_tags": {"tag": str(inventory_tags)}
                    }
                return {
                    "host_tags": instance_.deleted_tags("rsyncd"),
                    "inventory_tags": {"tag": str(inventory_tags)}
                }

    def update_host(self, items: list, checktype: str):
        for item in self.is_host(items):
            hosts = self.zapi.get_hts(
                output=["host"],
                hostids=jmes_search(
                    jmes_rexp=get_value(section="JMES", option="SEARCH_HOSTIDS"),
                    data=item.get("hosts")
                ),
                selectinventory="extend",
                selecttags=["tag", "value"],
                selecthostdiscovery="extend"
            )
            for host in hosts:
                inventory = self.inventory(item=item, host=host, check_type=checktype)
                if checktype == "inventory_type" and inventory:
                    update_params = {
                        "hostid": host["hostid"],
                        "inventory": inventory.get("inventory_tags"),
                        "tags": inventory.get("host_tags")
                    }
                    # 如 inventory mode 为禁用, 则改为自动
                    if host.get("inventory").get("inventory_mode") == "-1":  # disabled
                        update_params["inventory_mode"] = "1"  # automatic
                    self.zapi.update_host(update_params)
                    logging.info("\033[32m成功更新主机 '%s'\033[0m", host.get("host"))
                if checktype == "inventory_tag" and inventory:
                    self.zapi.update_host(
                        {
                            "hostid": host["hostid"],
                            "tags": inventory.get("host_tags"),
                            "inventory": inventory.get("inventory_tags")
                        }
                    )
                    logging.info("\033[32m成功更新主机 '%s'\033[0m", host.get("host"))

    def update_type(self):
        items = self.zapi.get_items(
            output=["lastvalue"],
            selecthosts=["host", "status"],
            filter_={"name": "Chassis Model"}
        )
        if items:
            self.update_host(items=self.is_vm(items), checktype="inventory_type")

    def update_tag(self):
        items = self.zapi.get_items(
            output=["lastclock", "lastvalue"],
            selecthosts=["host", "status"],
            search={"key_": get_value(section="ZABBIX", option="RSYNCD_ITEM")}
        )
        if items:
            self.update_host(items=items, checktype="inventory_tag")


def main(args):
    zapi = args.zapi
    UpdateHtInventory(zapi).update_tag()
    UpdateHtInventory(zapi).update_type()


parser = argparse.ArgumentParser()
parser.set_defaults(handler=main)
