#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Gary
# Datetime: 2022/12/19 17:42
# IDE: PyCharm
"""
    根据关键词获取 Zabbix 自动发现规则中的 "ICMP ping" 和 "Zabbix agent" 类型的主机信息并导出为 Execl 表格。
"""
import argparse
from ast import literal_eval
import logging
import os
import pandas as pd
from lib.utils.zbxapis import ZabbixApiGet
from lib.utils.format import jmes_search, to_excel_
from lib.utils.format import re_search, re_findall, get_value, pretty_tbl


def show(res):
    """
        打印出 Zabbix Discovery Hosts 信息：
    :param res:
    :return:
    """
    field_names = literal_eval(get_value(section="ZABBIX", option="DF_CH_FIELD_NAMES"))
    tbl = pretty_tbl(
        title="Zabbix Discovery Hosts Info",
        field_names=field_names,
        rows=res.values.tolist()
    )
    for field in field_names:
        tbl.align[field] = "l"
    print(tbl)


class ZbxDservices:
    def __init__(self, zapi, drule: str):
        self.zapi = zapi
        self.drule = drule

    @property
    def discovery_rules(self):
        """
            根据【关键字】搜索 Zabbix 自动发现规则：
        :return:
        """
        return self.zapi.get_drules(
            output="extend",
            selectdchecks="extend",
            selectdhosts="extend",
            search={"name": self.drule},
            searchwildcardsenabled=True
        )

    @property
    def dservices(self):
        """
            根据【自动发现规则 id】 获取所有已被发现的服务：
        :return:
        """
        return self.zapi.get_dservices(
            output=["dcheckid", "ip", "status", "value", "dhostid"],
            druleids=jmes_search(
                jmes_rexp=get_value(
                    section="JMES",
                    option="SEARCH_DRULEIDS"
                ),
                data=self.discovery_rules
            ),
            selectDRules=["name"],
            selectHosts=["host", "status"]
        )

    @property
    def hyperv_hosts(self):
        """
            获取 Zabbix "Hypervisors" 主机组下所有主机的【主机名】：
        :return:
        """
        return jmes_search(
            jmes_rexp=get_value(
                section="JMES",
                option="SEARCH_HOSTGROUP_HOSTS_HOSTNAME"
            ),
            data=self.zapi.get_ht_grps(
                output=["groupid", "name"],
                filter_={"name": ["Hypervisors"]},
                selecthosts=["name"]
            )
        )

    def get_check_ids(self, type_: str):
        """
            获取自动发现规则的 【dcheckid】：
                1. ICMP ping 类型的 "Type" 为 "12"；
                2. Zabbix agent 类型的 "Type" 为 "9"。
        :return:
        """
        return jmes_search(
            jmes_rexp=get_value(
                section="JMES",
                option="SEARCH_CHECK_IDS",
                raw=True
            ) % type_,
            data=self.discovery_rules
        )

    def get_hosts(self, filter_: dict):
        """
            根据过滤条件获取主机的 Inventory 信息：
        :param filter_:
        :return:
        """
        return self.zapi.get_hts(
            filter_=filter_,
            selectInventory=["poc_1_name", "os_short"]
        )


def make_discover_data(args):
    """
        生成 "ICMP ping" 类型和 "Zabbix agent" 类型的自动发现规则下的主机数据：
    :param args:
    :return:
    """
    instance_ = ZbxDservices(ZabbixApiGet(args.zapi), args.drule)
    df = pd.DataFrame(
        columns=literal_eval(get_value(section="ZABBIX", option="DISCOVER_HOST_FIELDS"))
    )
    for dservice in instance_.dservices:
        info = {}
        # Zabbix "ICMP ping" Check
        if dservice["dcheckid"] in instance_.get_check_ids("12"):
            info["dhostid"] = dservice.get("dhostid")
            info["check_type"] = "icmp"
            info["ipv4"] = dservice.get("ip")
            if dservice["hosts"]:
                info["monitored"] = "是"
                info["host"] = dservice.get("hosts")[0].get("host")
                info["status"] = ("启用" if dservice.get("hosts")[0].get("status") == "0" else "禁用")
            elif dservice["ip"] in instance_.hyperv_hosts:
                zbx_host = instance_.get_hosts({"name": dservice["ip"]})[0]
                info["monitored"] = "是"
                info["host"] = zbx_host.get("host")
                info["status"] = ("启用" if zbx_host.get("status") == "0" else "禁用")
                info["poc"] = zbx_host.get("inventory").get("poc_1_name")
                info["os"] = zbx_host.get("inventory").get("os_short")
        # Zabbix "Zabbix agent" Check
        if dservice["dcheckid"] in instance_.get_check_ids("9"):
            info["dhostid"] = dservice.get("dhostid")
            info["check_type"] = "agent"
            info["ipv4"] = dservice.get("ip")
            host = instance_.get_hosts({"host": dservice.get("value")})
            if host:
                zbx_host = host[0]
                info["host"] = dservice.get("value")
                info["monitored"] = "是"
                info["status"] = ("启用" if dservice.get("status") == "0" else "禁用")
                info["poc"] = zbx_host.get("inventory").get("poc_1_name")
                info["os"] = zbx_host.get("inventory").get("os_short")
        if info:
            # rule name 符合 "总类-业务网类-负责人" 形式，提取出业务网络和负责人信息
            drule_name = dservice.get("drules")[0].get("name")
            rexp = get_value(section="REXP", option="PERSON_IN_CHARGE")
            if re_search(rexp, drule_name):
                _, net, poc = re_findall(rexp, drule_name)[0]
                # 如从 inventory 中取到了 POC, 则优先使用, 否则使用 rule name 中的负责人
                info["poc"] = info.get("poc") if info.get("poc") else poc
                info["net"] = net
            df = df.append(pd.Series(info), ignore_index=True)
    # 既有 icmp check 又有 agent check 的情况, dhostid 相同, 通过 check_type 排序后
    # 去除 icmp check 的那一行数据, 以 agent check 为准
    df = df.sort_values(
        by=["dhostid", "check_type"],
        ascending=False
    ).drop_duplicates(subset="dhostid", keep="last")
    return df


def main(args):
    """
        利用 Pandas 处理自动发现服务的数据并导出为 Execl 文件：
    :param args:
    :return:
    """
    df = make_discover_data(args)
    # 按照 host 进行 group by, 其余字段进行单元格合并(仅 host 不为空的行参与)
    # 如果同一 host 有多个不同 ipv4, 则认为是多网卡(有可能是一张物理网卡使用多个 ip)
    df2 = df.groupby("host", as_index=False).apply(
        lambda x: pd.Series(
            {
                "ipv4": ",".join(x.ipv4.unique()),
                "monitored": ",".join([i for i in x.monitored.unique() if isinstance(i, str)]),
                "status": ",".join([i for i in x.status.unique() if isinstance(i, str)]),
                "multi_inf": ("是" if x.ipv4.count() > 1 else "否"),
                "net": ",".join([i for i in x.net.unique() if isinstance(i, str)]),
                "poc": ",".join([i for i in x.poc.unique() if isinstance(i, str)]),
                "os": ",".join([i for i in x.os.unique() if isinstance(i, str)]),
            }
        )
    )
    # 将 df 中 host 为空的数据与 df2 拼接在一起
    # drop 参数避免将旧索引添加为列
    res = df[df.host.isna()].drop(
        columns=["dhostid", "check_type"],
        axis=1
    ).append(df2).reset_index(drop=True)
    res.sort_values(by=["host"], na_position="last", inplace=True)
    res.monitored.fillna(value="否", inplace=True)
    res.multi_inf.fillna(value="否", inplace=True)
    # 字段重命名为中文
    res.rename(
        columns=literal_eval(get_value(section="ZABBIX", option="DF_CH")),
        inplace=True
    )
    show(res)
    if args.output:
        suffix = get_value(section="EXCEL", option="EXCEL_SUFFIX")
        fname = args.output if args.output.endswith(suffix) else args.output + suffix
        to_excel_(
            df=res,
            fname=fname,
            shname="discovery数据"
        )
        if os.path.exists(fname):
            logging.info("\033[32m成功导出 Excel 文件：%s\033[0m", os.path.abspath(fname))


parser = argparse.ArgumentParser(
    description="Get Zabbix 'Discovery' type host's info and export it as EXECL file"
)
parser.add_argument(
    "-r",
    "--drule",
    type=str,
    help="discovery rule"
)
parser.add_argument(
    "-o",
    "--output",
    help="output save to an excel file, xx.xlsx"
)
parser.set_defaults(handler=main)
