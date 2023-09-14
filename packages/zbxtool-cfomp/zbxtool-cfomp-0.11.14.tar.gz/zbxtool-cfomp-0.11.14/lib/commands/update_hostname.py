#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Gary
# Datetime: 2022/12/19 20:45
# IDE: PyCharm
"""
    更正自动发现主机的主机名。
"""
import argparse
import logging
from lib.utils.zbxapis import ZabbixApiUpdate
from lib.utils.format import re_search, re_sub, get_value


def main(args):
    """
        过滤出 Hostname 以 "_x" 结尾的主机, 并修改 Hostname：
    :param args:
    :return:
    """
    zapi = ZabbixApiUpdate(args.zapi)
    hosts = zapi.get_hts(
        output=["hostid", "host"],
        groupids=[
            zapi.get_ht_grps(
                filter_={"name": "Discovered hosts"},
                output=["groupid"]
            )[0].get("groupid")
        ],
        search={"host": "_"}
    )
    if hosts:
        for host in hosts:
            rexp = get_value(section="REXP", option="HOSTNAME")
            old_hostname = host.get("host")
            if re_search(rexp, old_hostname):
                new_hostname = re_sub(rexp, "", old_hostname)
                zapi.update_host(
                    {
                        "hostid": host.get("hostid"),
                        "host": new_hostname
                    }
                )
                logging.info(
                    "\033[32m更新主机名成功: hostid=%s, hostname => %s => %s\033[0m",
                    host.get("hostid"),
                    old_hostname,
                    new_hostname
                )


parser = argparse.ArgumentParser()
parser.set_defaults(handler=main)
