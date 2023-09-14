#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    通过 vCenter Server 主机更新 Zabbix ESXI 类型主机的 Host Inventory 信息。
"""
import argparse
import sys
import logging
from urllib.parse import urlparse
from lib.utils.zbxtags import HostTags, InventoryTagDict
from lib.utils.esxiapis import VMManger


class UpdateZbxHost:
    """Mainly used to update the host inventory of zabbix 'ESXI' type host"""

    def __init__(self, zapi):
        self._zapi = zapi

    @property
    def esxi_hosts(self):
        """
            用来根据模板的 tag 获取 Zabbix 主机的具体信息：
                1. 获取到的 Zabbix 主机信息包括 Inventory、Macro、Host Tags、Discoveries 等。
        :return:
        """
        return self._zapi.host.get(
            {
                "output": ["hostid", "name", "inventory_mode", "flags"],
                "tags": [
                    {"tag": "target", "value": "vmware"},
                    {"tag": "target", "value": "vmware-hypervisor"}
                ],
                # Return hosts that have given tags also in all of their linked templates
                # True - linked templates must also have given tags
                # False - (default) linked template tags are ignored
                "inheritedTags": True,
                "selectMacros": ["macro", "value"],
                "selectInventory": "extend",
                "selectTags": ["tag", "value"],
                "selectHostDiscovery": "extend"
            }
        )

    @staticmethod
    def get_update_params(inventory: dict, host: dict):
        """
            用来获取 Zabbix 主机更新需要的字段信息：
                1. 首先是 Host Inventory，ESXI 类型主机的 Host Inventory 信息主要通过 vCenter Server 获取；
                2. 标签信息分为两种情况：
                    2.1 如果主机是自动发现类型的主机，Zabbix Api 接口提示自动发现主机是不能添加 Host Tags 的，
                        那就只能添加 Host Inventory Tag；
                    2.2 如果主机不是自动发现类型的主机，则可以添加 Host Tags，Host Inventory Tag 则不再添加。
        :param inventory:
        :param host:
        :return:
        """
        # flags: 0 - a plain host;4 - a discovered host
        if host.get("flags") == "4":
            inventory_tags = InventoryTagDict(host.get("inventory").get("tag"))
            inventory_tags["Esxi"] = None
            inventory.update({"tag": str(inventory_tags)})
            return {
                "hostid": host.get("hostid"),
                "inventory": inventory
            }
        return {
            "hostid": host.get("hostid"),
            "tags": HostTags(host.get("tags")).added_tags(
                tag_name="Esxi",
                tag_value=""
            ),
            "inventory": inventory
        }

    @staticmethod
    def get_esxi_info(vcenter_ip: str, host: dict):
        """
            根据 vCenter Server 获取 ESXI 主机信息：
        :param vcenter_ip:
        :param host:
        :return:
        """
        username = [
            macro for macro in host.get("macros")
            if macro.get("macro") == r"{$VMWARE.USERNAME}"
        ]
        password = [
            macro for macro in host.get("macros")
            if macro.get("macro") == r"{$VMWARE.PASSWORD}"
        ]
        if username and password:
            return VMManger(
                host=vcenter_ip,
                user=username[0].get("value"),
                passwd=password[0].get("value")
            ).fetch_esxi(esxi_name=host.get("name"))


def main(args):
    """Main Function"""
    zapi = args.zapi
    zbx = UpdateZbxHost(zapi)
    if not zbx.esxi_hosts:
        sys.exit()
    hosts = zbx.esxi_hosts
    # 如指定 limit 参数, 则仅处理列表中的 host
    if args.limit:
        hosts = [ht for ht in zbx.esxi_hosts if ht.get("name") in args.limit]
    # 调用 zapi 查询 host 的 macros 信息
    for host in hosts:
        url = [
            macro for macro in host.get("macros")
            if macro.get("macro") == r"{$VMWARE.URL}"
        ]
        if url:
            vcenter_url = urlparse(url[0].get("value")).hostname
            logging.info(
                "\033[32m搜索 ESXI 主机成功，vCenter => '%s', ESXI Host => '%s'\033[0m",
                vcenter_url,
                host.get("name")
            )
            update_params = zbx.get_update_params(
                inventory=zbx.get_esxi_info(vcenter_ip=vcenter_url, host=host),
                host=host
            )
            if host["inventory_mode"] == "-1":  # disabled
                update_params["inventory_mode"] = "1"  # Auto
            zapi.host.update(update_params)
            logging.info(
                "\033[32mESXI主机Inventory信息更新成功，Host => '%s'\033[0m",
                host.get("name")
            )


parser = argparse.ArgumentParser()
parser.add_argument(
    "-l",
    "--limit",
    action="append",
    help="Specify ip address of 'ESXI' type hosts"
)
parser.set_defaults(handler=main)
