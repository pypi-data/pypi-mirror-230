#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Gary
# Datetime: 2022/12/19 19:53
# IDE: PyCharm
"""
    依据现有的机房网段信息对 Zabbix 主机的 Interfaces(即主机 IP 信息)进行各种操作：
        1. --check_agent, 过滤出 IP 地址不存在于主机资产 host_networks 中的 agent interface；
        2. --add_extra, 将 --check_agent 过滤出的额外的主机地址添加到 host agent interface；
        3. --delete_extra, 如果主机存在多个 agent interface，只保留第一个 agent interfaces，其余的全部删除；
        4. --delete_invaild, 删除主机中无效的 agent interfaces。
"""
import argparse
import re
import logging
import sys
from ast import literal_eval
import pandas as pd
from lib.utils.zbxapis import ZabbixApiGet, ZabbixApiCreate, ZabbixApiDel
from lib.utils.format import jmes_search, to_excel_, pretty_tbl
from lib.utils.format import get_value, re_search, re_findall, IPS


def show(res):
    """
        打印出 Zabbix Discovery Hosts 信息：
    :param res:
    :return:
    """
    field_names = literal_eval(get_value(section="ZABBIX", option="INTERFACES_DATA_COLUMNS"))
    tbl = pretty_tbl(
        title="Zabbix Host Interfaces",
        field_names=field_names,
        rows=res.values.tolist()
    )
    for field in field_names:
        tbl.align[field] = "l"
    print(tbl)


def save_to_excel(df: pd.DataFrame, fname: str):
    suffix = get_value(section="EXCEL", option="EXCEL_SUFFIX")
    if not fname.endswith(suffix):
        fname = fname + suffix
    to_excel_(df, fname)
    logging.info("\033[32m成功保存文件：%s\033[0m", fname)


class ZbxInterfaces:
    def __init__(self, zapi, check_file: str):
        self._zapi = zapi
        self.check_file = check_file

    @staticmethod
    def get_agent_ips(host: dict):
        """
            获取 zabbix agent interface ip：
        :param host:
        :return:
        """
        return jmes_search(
            jmes_rexp=get_value(
                section="JMES",
                option="SEARCH_AGENT_IPS"
            ),
            data=host.get("interfaces")
        )

    @staticmethod
    def get_host_networks(host: dict):
        """
            获取 host inventory 中 host_networks 里面的 ip 地址：
        :param host:
        :return:
        """
        if isinstance(host.get("inventory"), list) and not host.get("inventory"):
            return set()
        if isinstance(host.get("inventory"), dict) and host.get("inventory"):
            os_full = host.get("inventory").get("os_full")
            networks = host.get("inventory").get("host_networks")
            search_win = re_search(
                rexp=get_value(section="REXP", option="WIN_HOST"),
                content=os_full,
                mode=re.I
            )
            search_linux = re_search(
                rexp=get_value(section="REXP", option="LINUX_HOST"),
                content=os_full,
                mode=re.I
            )
            if search_win:
                host_networks = set(
                    re_findall(
                        rexp=get_value(section="REXP", option="WIN_IP"),
                        content=networks,
                        mode=re.M
                    )
                )
            elif search_linux:
                host_networks = set(
                    re_findall(
                        rexp=get_value(section="REXP", option="LINUX_IP"),
                        content=networks,
                        mode=re.M
                    )
                )
            else:
                host_networks = set()
            return host_networks

    @property
    def zbx_hosts(self):
        return ZabbixApiGet(self._zapi).get_hts(
            output=["name", "hostid", "proxy_hostid"],
            selectinventory=["inventory_mode", "location", "host_networks", "os_full", "os_short"],
            selectinterfaces=["interfaceid", "ip", "type", "main"]
        )

    def get_other_ips(self, host: dict):
        """
            获取额外的 IP：
                1. inventory 中 host_networks 里面的 ip 排除掉 agent_ips；
                2. 再排除掉不在 IDC_NETWORKS 网段内的 ip；
                3. 即不是 agent ip，并且此 IP 在 IDC_NETWORKS 网段内。
        :param host:
        :return:
        """
        instance_ = IPS(self.check_file)
        other_ips = list(
            self.get_host_networks(host) - set(self.get_agent_ips(host))
        )
        return [ip for ip in other_ips if instance_.valid_ip(ip)]

    def delete_invaild(self, host: dict):
        """
            删除 ip 不在 host_networks 中的非第一个 agent interface：
        :param host:
        :return:
        """
        host_networks = self.get_host_networks(host)
        if host_networks:
            for inf in host.get("interfaces")[::-1]:
                # type - 1 - agent
                # main - 1 - default
                if inf.get("type") == "1" and inf.get("main") != "1":
                    if inf.get("ip") in host_networks:
                        continue
                    ZabbixApiDel(self._zapi).del_interface([inf.get("interfaceid")])
                    logging.info(
                        "\033[32m成功删除非法 Interface: host =>'%s', agent_ip =>'%s'\033[0m",
                        host.get("name"),
                        inf.get("ip")
                    )
                    host.get("interfaces").remove(inf)

    def delete_extra(self, host: dict):
        """
            指定了 --delete_extra, 只保留第一个 agent interfaces，其余的全部删除：
        :param host:
        :return:
        """
        for inf in host.get("interfaces")[::-1]:
            if inf.get("type") == "1" and inf.get("main") != "1":
                ZabbixApiDel(self._zapi).del_interface([inf.get("interfaceid")])
                logging.info(
                    "\033[32m成功删除额外 Interface: host =>'%s', agent_ip =>'%s'\033[0m",
                    host.get("name"),
                    inf.get("ip")
                )
                host.get("interfaces").remove(inf)

    def add_extra(self, host: dict):
        """
            将额外的主机地址添加到 host agent interface：
        :param host:
        :return:
        """
        for other_ip in self.get_other_ips(host):
            ZabbixApiCreate(self._zapi).create_ht_interface(
                hostid=host.get("hostid"),
                ip_=other_ip
            )
            logging.info(
                "\033[32m成功添加 Interface: host =>'%s', extra_ip =>'%s'\033[0m",
                host.get("name"),
                other_ip
            )
            host.get("interfaces").append({"main": "0", "type": "1", "ip": other_ip})

    def check_agent(self, host: dict):
        """
            打印 agent interface IP 地址不存在于主机资产的 host_networks 的信息：
        :param host:
        :return:
        """
        host_networks = self.get_host_networks(host)
        if not host_networks:
            logging.debug(
                "\033[33m主机 '%s' 没有 host_networks，跳过\033[0m",
                host.get("name")
            )
            return []
        if host_networks:
            return [ip for ip in self.get_agent_ips(host) if ip not in host_networks]


def main(args):
    instance_ = ZbxInterfaces(args.zapi, args.check_file)
    # 生成 pandas 数据表, 用来输出屏幕和保存文件
    df = pd.DataFrame(
        columns=literal_eval(get_value(section="ZABBIX", option="INTERFACES_DATA_COLUMNS"))
    )
    for host in instance_.zbx_hosts:
        # 指定了 --delete_invaild, 删除主机中无效的 agent interfaces
        if args.delete_invaild:
            instance_.delete_invaild(host)
        # 指定了 --delete_extra, 只保留第一个 agent interfaces，其余的全部删除
        if args.delete_extra:
            instance_.delete_extra(host)
        # 指定了 --add_extra, 将额外的主机地址添加到 host agent interface
        if args.add_extra:
            instance_.add_extra(host)
        # 指定了 --check_agent, 过滤出 IP 地址不存在于主机资产的 agent interface
        if args.check_agent:
            agent_ips = instance_.check_agent(host)
            if not agent_ips:
                logging.debug(
                    "\033[33m主机 '%s' 所有的 'interface' 都在 host_networks\033[0m",
                    host.get("name")
                )
                continue
        else:
            agent_ips = instance_.get_agent_ips(host)
        # 添加数据到数据表
        if isinstance(host.get("inventory"), dict) and instance_.get_other_ips(host):
            df.loc[len(df)] = [
                host.get("name"),
                host.get("inventory").get("os_short"),
                host.get("inventory").get("location"),
                ",".join(agent_ips),
                ",".join(instance_.get_other_ips(host))
            ]
    # 将结果按 location 排序
    res = df.sort_values(by=["location"], na_position="last").reset_index(drop=True)
    if res.empty:
        logging.info("No data retrieved.")
        sys.exit(1)
    if args.dump and args.dump == "excel":
        save_to_excel(res, "results.xlsx")
    elif args.dump == "console" and not args.delete_invaild and not args.delete_extra:
        show(res)


parser = argparse.ArgumentParser(description="find ip from host inventory")
parser.add_argument("-f", "--check_file", required=True, help="a list of ip range of each IDC")
parser.add_argument(
    "--dump",
    choices=["console", "excel"],
    default="console",
    help="Print to screen, or save to excel"
)
parser.add_argument("--check_agent", action="store_true", help="display invalid interface")
parser.add_argument("--delete_invaild", action="store_true", help="delete invaild interface")
parser.add_argument("--add_extra", action="store_true", help="add extra ip to interface")
parser.add_argument("--delete_extra", action="store_true", help="delete extra ip from interface")
parser.set_defaults(handler=main)
