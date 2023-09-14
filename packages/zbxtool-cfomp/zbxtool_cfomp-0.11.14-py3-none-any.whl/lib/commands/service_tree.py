#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Gary
# Datetime: 2022/12/19 20:18
# IDE: PyCharm
"""
    依据 zabbix 主机组生成/删除 it-service 树。
"""
import argparse
import logging
import sys
from lib.utils.zbxapis import ZabbixApiCreate, ZabbixApiDel
from lib.utils.format import jmes_search, get_value


class CreateItService:
    def __init__(self, zapi, service_name: str, group_name: str):
        self.zapi = ZabbixApiCreate(zapi)
        self.service_name = service_name
        self.group_name = group_name

    def get_sla_tag(self, sla_name: str):
        """
            获取 Zabbix SLA 中的 Service tags：
                1. 区别于 Zabbix 4.0 及更老版本，在 Zabbix 6.0 中不能直接指定 SLA，
                  而是需要先在 SLA 中添加 Service tags，
                  然后再在 Service 中添加此 Service tag 才可以将两者关联起来。
        :param sla_name:
        :return:
        """
        sla = self.zapi.get_sla(
            output=["slaid", "name"],
            selectservicetags=["tag", "value"],
            filter_={"name": sla_name}
        )
        if sla and sla[0].get("service_tags"):
            return sla[0].get("service_tags")
        if not sla or not sla[0].get("service_tags"):
            logging.info(
                "\033[32mSLA '%s' 不存在，或者不存在 'service tag'\033[0m",
                sla_name
            )
            return []

    def create(self, prb_tag_name: str, sla_name: str):
        """
            根据 Problem 的标签名称和 SLA 名称创建 Service：
                1. 在 Zabbix 老版本中是可以直接指定 trigger id 的，由此可以将 Service 和 Event 告警事件关联起来，
                   但是在 Zabbix 6.0 版本中，在创建 Service 时必须要指定 Problem 的 tag 名称，
                   只要这样才可以将 Service 和 Event 告警事件关联起来。
        :param prb_tag_name:
        :param sla_name:
        :return:
        """
        sla = self.zapi.get_sla(
            output=["slaid", "name"],
            selectservicetags=["tag", "value"],
            filter_={"name": sla_name}
        )
        if sla and sla[0].get("service_tags"):
            rootsrv = self.zapi.get_service(filter_={"name": self.service_name})
            if rootsrv:
                logging.info(
                    "\033[32mService '%s'已经存在，默认不做操作\033[0m",
                    self.service_name
                )
                return
            rootsrv = self.zapi.create_service(
                service_name=self.service_name,
                tags=self.get_sla_tag(sla_name)
            )
            hosts = self.zapi.get_hts(
                output=["name"],
                groupids=jmes_search(
                    jmes_rexp=get_value(section="JMES", option="SEARCH_GROUPIDS"),
                    data=self.zapi.get_ht_grps(
                        output=["groupid"],
                        filter_={"name": self.group_name}
                    )
                ),
                selecttriggers="extend"
            )
            for host in hosts:
                hostsrv = self.zapi.create_service(
                    service_name=host.get("name"),
                    parents=[{"serviceid": rootsrv.get("serviceids")[0]}],
                    tags=self.get_sla_tag(sla_name)
                )
                for trigger in host.get("triggers"):
                    self.zapi.create_service(
                        service_name=trigger.get("description"),
                        parents=[{"serviceid": hostsrv.get("serviceids")[0]}],
                        problem_tags=[{"tag": prb_tag_name, "operator": 2, "value": ""}],
                        tags=self.get_sla_tag(sla_name)
                    )
            logging.info("\033[33m成功创建 Service '%s'\033[0m", self.service_name)


class DeleteItService:
    def __init__(self, zapi, service_name):
        self.zapi = ZabbixApiDel(zapi)
        self.service_name = service_name

    def hard_service_delete(self, service):
        """
            删除一个 Service 及其下的所有的子 Service：
                1. 在删除 Zabbix Service 时，如果只删除此 Service 只会将这个 Service 本身删除，
                   但是这个 Service 下面的子 Service 以及递归的 Service 却并不会删除，
                   所有要递归删除下面的所有 Service。
        :param service:
        :return:
        """
        for node in service.get("children"):
            tmpsrvs = self.zapi.get_service(
                serviceids=node.get("serviceid"),
                selectchildren="extend"
            )
            for tmpsrv in tmpsrvs:
                self.hard_service_delete(tmpsrv)
        self.zapi.del_service([service.get("serviceid")])

    def delete(self):
        rootsrvs = self.zapi.get_service(
            filter_={"name": self.service_name},
            selectchildren="extend"
        )
        for rootsrv in rootsrvs:
            self.hard_service_delete(rootsrv)
        logging.info(
            "\033[33m成功删除 Service '%s'\033[0m",
            self.service_name
        )


def main(args):
    if args.action == "create":
        if not args.group_name or not args.tag_name or not args.sla_name:
            parser.print_help()
            logging.error("the argument --group-name/--tag-name/--sla-name is required")
            sys.exit(1)
        CreateItService(args.zapi, args.service_name, args.group_name).create(
            args.tag_name,
            args.sla_name
        )
    if args.action == "delete":
        DeleteItService(args.zapi, args.service_name).delete()


parser = argparse.ArgumentParser(description="Create or delete zabbix service tree")
parser.add_argument("action", choices=["create", "delete"], help="Create/Delete IT service Tre")
parser.add_argument(
    "-n",
    "--service-name",
    required=True,
    help="The Name of IT service Tree's root"
)
parser.add_argument("-g", "--group-name", help="Create IT service tree from the Group")
parser.add_argument("-t", "--tag-name", help="Problem tag name")
parser.add_argument("-s", "--sla-name", help="Zabbix SLA name")
parser.set_defaults(handler=main)
