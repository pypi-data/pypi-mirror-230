#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    根据 Inventory type 搜索 "Server" 和 "BMC" 主机，获取主机的序列号，如果两台主机的序列号可以匹配的上，则进行以下操作：
        1. "Server" 类型主机添加 "auto_oob" 标签，
           且主机的 Inventory OOB IP address 字段设置为 Mgnt Servers 主机 snmp interface 地址；
        2. "BMC" 类型主机添加 "auto_server" 标签。
"""
import argparse
import logging
from lib.utils.zbxtags import HostTags


class OOB:
    def __init__(self, zapi):
        self._zapi = zapi

    @property
    def server_bmc_hosts(self):
        """
            根据 Host Inventory Type 获取 "Server" 类型和 "BMC" 类型的主机信息：
        :return:
        """

        def get_hosts_by_inventory_type(inventory_type):
            return list(
                filter(
                    lambda x: len(x.get("inventory").get("serialno_a")) and len(x.get("interfaces")),
                    self._zapi.host.get(
                        {
                            "output": ["hostid", "name", "flags"],
                            "selectInventory": ["tag", "serialno_a"],
                            "selectInterfaces": ["type", "main", "ip"],
                            "searchInventory": {"type": inventory_type},
                            "selectTags": ["tag", "value"]
                        }
                    )
                )
            )

        return get_hosts_by_inventory_type("Server"), get_hosts_by_inventory_type("BMC")

    def update(self, hostid: str, flags=None, host_tags=None, oob_ip=None):
        """
            更新主机信息：
                1. 主要更新 Host Tags、Inventory Tags、Inventory OOB IP address。
        :param hostid:
        :param flags:
        :param host_tags:
        :param oob_ip:
        :return:
        """
        # flags: 0 - a plain host;4 - a discovered host
        if flags == "4":
            self._zapi.host.update(
                {
                    "hostid": hostid,
                    "inventory": {
                        "oob_ip": oob_ip
                    }
                }
            )
        else:
            self._zapi.host.update(
                {
                    "hostid": hostid,
                    "tags": host_tags,
                    "inventory": {
                        "oob_ip": oob_ip
                    }
                }
            )

    def search_hosts(self, tag_name: str):
        """
            根据标签名搜索主机信息：
                1. Zabbix 6.0 版本支持 Host tag，但以往的旧版本主机是依据 Host Inventory tag，所以需要分两种情况；
                    1.1 自动发现类型的主机，Zabbix Api 接口提示自动发现主机是不能添加 Host Tags 的，
                        所以只能在 Host Inventory Tag 添加，因而只能根据 Host Inventory Tag 搜索；
                    1.2 不属于自动发现类型的主机，Host 是可以添加 tag 的，因而根据 Host Tags 搜索。
        :param tag_name:
        :return:
        """
        hosts = []
        hosts_no_discovery = self._zapi.host.get(
            {
                "output": ["hostid", "host"],
                "selectInventory": ["tag", "oob_ip"],
                "searchInventory": {"tag": tag_name},
                "selectTags": ["tag", "value"]
            }
        )
        hosts_with_discovery = self._zapi.host.get(
            {
                "output": ["hostid", "host"],
                "selectInventory": ["tag", "oob_ip"],
                "tags": [{"tag": tag_name}],
                "selectTags": ["tag", "value"]
            }
        )
        for host in hosts_no_discovery + hosts_with_discovery:
            if host not in hosts:
                hosts.append(host)
        if hosts:
            tag_hosts = [ht for ht in hosts if HostTags(ht.get("tags")).have(tag_name)]
            inventory_tag_hosts = [
                ht for ht in hosts if
                isinstance(ht.get("inventory"), dict)
                and "auto_oob" in ht.get("inventory").get("tag")
            ]
            return tag_hosts + inventory_tag_hosts

    def rm_auto_oob_tag(self):
        """
            清除 "Server" 类型主机的 "auto_oob" 标签：
        :return:
        """
        hosts = self.search_hosts("auto_oob")
        if hosts:
            for host in hosts:
                self.update(
                    hostid=host.get("hostid"),
                    host_tags=HostTags(host.get("tags")).deleted_tags("auto_oob")
                )
                logging.info(
                    "\033[32m成功删除主机 '%s' 的 oob_ip 和 'auto_oob' 标签\033[0m",
                    host.get("host")
                )

    def rm_auto_server_tag(self):
        """
            清除 "BMC" 类型主机的 "auto_server" 标签：
        :return:
        """
        hosts = self.search_hosts("auto_server")
        for host in hosts:
            self.update(
                hostid=host.get("hostid"),
                host_tags=HostTags(host.get("tags")).deleted_tags("auto_server")
            )
            logging.info(
                "\033[32m成功删除主机 '%s' 的 'auto_server' 标签\033[0m",
                host.get("host")
            )

    def handle_hosts_tag(self):
        """
            给 "Server" 和 "BMC" 类型的主机添加 "auto_oob" 和 "auto_server" 标签：
        :return:
        """
        server_hosts, bmc_hosts = self.server_bmc_hosts
        logging.info(
            "\033[32m获取到 %d 台 'Server' 类型主机，%d 台 'BMC' 类型主机\033[0m",
            len(server_hosts),
            len(bmc_hosts)
        )
        server_serials = [
            host.get("inventory").get("serialno_a")
            for host in server_hosts if isinstance(host.get("inventory"), dict)
        ]
        bmc_serials = [
            host.get("inventory").get("serialno_a")
            for host in bmc_hosts if isinstance(host.get("inventory"), dict)
        ]
        match = list(set(server_serials) & set(bmc_serials))
        logging.info(
            "\033[32m在 'Server' 类型主机和 'BMC' 类型主机之间总共匹配到 %d 个 'serialno'\033[0m",
            len(match)
        )
        if match:
            for serialno in match:
                server_host = [
                    host for host in server_hosts
                    if host.get("inventory").get("serialno_a") == serialno
                ][0]
                bmc_host = [
                    host for host in bmc_hosts
                    if host.get("inventory").get("serialno_a") == serialno
                ][0]
                logging.info(
                    "\033[32m在 'Server' 类型主机 '%s' 和 'BMC' 类型主机 '%s' 之间成功匹配 serialno_a '%s'\033[0m",
                    server_host.get("name"),
                    bmc_host.get("name"),
                    serialno
                )
                # 更新 Server 主机清单的 tag 和 oob_ip 字段
                if bmc_host.get("interfaces"):
                    self.update(
                        hostid=server_host.get("hostid"),
                        flags=server_host.get("flags"),
                        host_tags=HostTags(server_host.get("tags")).added_tags("auto_oob", ""),
                        oob_ip=bmc_host.get("interfaces")[0].get("ip")
                    )
                # 更新 BMC 主机清单的 tag 字段
                if server_host.get("interfaces"):
                    self.update(
                        hostid=bmc_host.get("hostid"),
                        host_tags=HostTags(bmc_host.get("tags")).added_tags(
                            "auto_server",
                            server_host.get("interfaces")[0].get("ip")
                        )
                    )


def main(args):
    """Main Function"""
    zapi = args.zapi
    # 清除实体服务器 inventory tag 字段中的 auto_oob 标识
    if args.rm_auto_oob:
        OOB(zapi).rm_auto_oob_tag()
    # 清除 BMC 的 inventory tag 字段中的 auto_server 标识
    if args.rm_auto_server:
        OOB(zapi).rm_auto_server_tag()
    # 设置 Server 的 auto_oob 和 BMC 的 auto_server inventory tag
    if args.tags:
        OOB(zapi).handle_hosts_tag()


parser = argparse.ArgumentParser(description="Matching inventory OOB IP address")
parser.add_argument(
    "-ro",
    "--rm_auto_oob",
    action="store_true",
    help="Remove auto_oob in inventory tag field and reset the oob_ip inventory field"
)
parser.add_argument(
    "-rs",
    "--rm_auto_server",
    action="store_true",
    help="Remove auto_server=x.x.x.x in inventory tag field"
)
parser.add_argument(
    "-t",
    "--tags",
    action="store_true",
    help="Make server and bmc host inventory tag"
)
parser.set_defaults(handler=main)
