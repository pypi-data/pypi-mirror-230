#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Gary
# Datetime: 2022/12/19 19:36
# IDE: PyCharm
"""
    添加、删除、显示、替换 Zabbix 主机/主机组所有主机模板。
"""
import argparse
import logging
import sys
from lib.utils.zbxapis import ZabbixApiUpdate
from lib.utils.format import pretty_tbl, jmes_search, get_value, DiskCache


def show(hosts_info: list):
    """
        打印出 Zabbix Templates 信息：
    :param hosts_info:
    :return:
    """
    tbl = pretty_tbl(
        title="Results of linked templates",
        field_names=["Host", "Templates"],
        rows=jmes_search(
            jmes_rexp=get_value(
                section="JMES",
                option="SEARCH_EACH_HOST_TEMPLATES"
            ),
            data=hosts_info
        )
    )
    tbl.align["Host"] = "l"
    tbl.align["Templates"] = "l"
    print(tbl)


class BaseTool:
    def __init__(self, args):
        self._zapi = ZabbixApiUpdate(args.zapi)
        self.hosts = args.hosts or [""]
        self.ht_grps = args.groups or [""]
        self._cache = DiskCache()

    @property
    def hosts_info(self):
        """
            获取 Zabbix 主机信息：
                1. 主要包含模板信息。
        :return:
        """
        if self.ht_grps:
            self.hosts.extend(
                jmes_search(
                    jmes_rexp=get_value(
                        section="JMES",
                        option="SEARCH_HOSTGROUP_HOSTS_HOST"
                    ),
                    data=self._zapi.get_ht_grps(
                        filter_={"name": self.ht_grps},
                        selecthosts=["host"]
                    )
                )
            )
        if self.hosts:
            return self._zapi.get_hts(
                filter_={"name": self.hosts},
                selectparenttemplates=["host"],
                output=["host"]
            )

    def get_templates_info(self, tpl_names: list):
        """
            获取 Zabbix 模板信息：
        :param tpl_names:
        :return:
        """
        tpl_info = []
        if tpl_names:
            for tpl_name in tpl_names:
                if self._cache.get_cache("tpl_" + tpl_name):
                    tpl_info.append(dict(self._cache.get_cache("tpl_" + tpl_name)))
                if not self._cache.get_cache("tpl_" + tpl_name):
                    tpl = self._zapi.get_tpls(
                        filter_={"host": tpl_name},
                        output=["host"]
                    )
                    self._cache.set_cache(
                        "tpl_" + tpl_name,
                        tpl[0],
                        expire=60
                    )
                    tpl_info.append(dict(self._cache.get_cache("tpl_" + tpl_name)))
            return tpl_info

    def if_tpl_exist(self, tpl_names: list):
        """
            判断指定的模板是否存在于 Zabbix 中：
        :param tpl_names:
        :return:
        """
        return [
            tpl_name
            for tpl_name in tpl_names if
            self._zapi.get_tpls(filter_={"host": tpl_name})
            and self._zapi.get_tpls(filter_={"host": tpl_name})[0]
        ]

    @staticmethod
    def filter_tpls(host: dict, templates, type_: str):
        """
            过滤 Zabbix 模板：
        :param host:
        :param templates:
        :param type_:
        :return:
        """
        parent_tpls = jmes_search(
            jmes_rexp=get_value(section="JMES", option="SEARCH_HOST_PARENTS_TEMPLATES"),
            data=host
        )
        if type_.lower() == "add":
            return [tpl for tpl in templates if tpl not in parent_tpls]
        if type_.lower() == "del" or type_.lower() == "rep":
            return [tpl for tpl in templates if tpl in parent_tpls]


class ListTemplate(BaseTool):
    def __init__(self, args):
        super().__init__(args)
        show(self.hosts_info)


class AddTemplate(BaseTool):
    def __init__(self, args):
        super().__init__(args)
        self.templates = args.add
        self.add()

    def add(self):
        """
            往 Zabbix 主机添加新模板：
                1. 这个新模板不能已经存在于 Zabbix 主机中，否则会报错。
        :return:
        """
        for host in self.hosts_info:
            tpls = self.filter_tpls(
                host=host,
                templates=self.if_tpl_exist(tpl_names=self.templates),
                type_="add"
            )
            if tpls:
                params = {
                    "hostid": host.get("hostid"),
                    "templates": self.get_templates_info(tpls) + host.get("parentTemplates")
                }
                self._zapi.update_host(params)
                logging.info(
                    "\033[32m成功更新主机 '%s'，添加新模板 => '%s'\033[0m",
                    host.get("host"),
                    "、".join([tpl for tpl in tpls if tpls])
                )
        show(self.hosts_info)


class ClearTemplate(BaseTool):
    def __init__(self, args):
        self.templates = args.clear
        super().__init__(args)
        self.clear()

    def clear(self):
        """
            删除 Zabbix 主机模板：
                1. 这个模板必须已经存在于 Zabbix 主机中，否则无法删除。
        :return:
        """
        for host in self.hosts_info:
            tpls = self.filter_tpls(
                host=host,
                templates=self.if_tpl_exist(tpl_names=self.templates),
                type_="del"
            )
            if tpls:
                params = {
                    "hostid": host.get("hostid"),
                    "templates_clear": self.get_templates_info(tpls)
                }
                self._zapi.update_host(params)
                logging.info(
                    "\033[32m成功更新主机 '%s'，删除模板 => '%s'\033[0m",
                    host.get("host"),
                    "、".join([tpl for tpl in tpls if tpls])
                )
        show(self.hosts_info)


class UseTemplate(BaseTool):
    def __init__(self, args):
        super().__init__(args)
        self.templates = args.use
        self.use()

    def use(self):
        """
            替换全部原来的 Zabbix 主机模板：
        :return:
        """
        for host in self.hosts_info:
            tpls = self.if_tpl_exist(tpl_names=self.templates)
            if tpls:
                params = {
                    "hostid": host.get("hostid"),
                    "templates": self.get_templates_info(tpls)
                }
                self._zapi.update_host(params)
                logging.info(
                    "\033[32m成功更新主机 '%s'\033[0m",
                    host.get("host")
                )
        show(self.hosts_info)


class ReplaceTemplate(BaseTool):
    def __init__(self, args):
        super().__init__(args)
        self.templates = args.replace
        self.instead_templates = args.to
        self.replace()

    def replace(self):
        """
            替换 Zabbix 主机模板：
                1. 被替换的模板必须已经存在于 Zabbix 主机中；
                2. 要替换的模板不能已经存在于 Zabbix 主机中。
        :return:
        """
        for host in self.hosts_info:
            tpls_del = self.filter_tpls(host=host, templates=self.templates, type_="rep")
            tpls_add = self.filter_tpls(
                host=host,
                templates=self.if_tpl_exist(tpl_names=self.instead_templates),
                type_="add"
            )
            if tpls_del and tpls_add:
                new_templates = list(
                    filter(
                        lambda tpl: tpl not in self.get_templates_info(self.templates),
                        host.get("parentTemplates")
                    )
                )
                new_templates += self.get_templates_info(self.instead_templates)
                params = {"hostid": host.get("hostid"), "templates": new_templates}
                self._zapi.update_host(params)
                logging.info(
                    "\033[32m成功更新主机 '%s', 替换模板 '%s' => 新模板 '%s'\033[0m",
                    host.get("host"),
                    "、".join([tpl for tpl in self.templates if self.templates]),
                    "、".join([tpl for tpl in self.instead_templates if self.instead_templates])
                )
        show(self.hosts_info)


def main(args):
    # 显示模板信息
    if args.list:
        ListTemplate(args)
    # 添加模板
    if args.add:
        AddTemplate(args)
    # 移除指定模板
    if args.clear:
        ClearTemplate(args)
    # 替换全部模板
    if args.use:
        UseTemplate(args)
    # 替换指定模板
    if args.replace:
        if not args.to:
            parser.print_help()
            logging.error("the argument --to is required")
            sys.exit(1)
        ReplaceTemplate(args)


parser = argparse.ArgumentParser(description="(list|add|del) zabbix hosts templates")
parser.add_argument(
    "--hosts",
    nargs="+",
    help="specific zabbix hosts"
)
parser.add_argument(
    "-g",
    "--groups",
    nargs="+",
    help="specific zabbix hostgroups"
)
parser.add_argument(
    "-t",
    "--to",
    nargs="+",
    help="specific templates names instead to"
)
opt_group = parser.add_mutually_exclusive_group(required=True)
opt_group.add_argument(
    "-l",
    "--list",
    action="store_true",
    help="list specific host templates"
)
opt_group.add_argument(
    "-a",
    "--add",
    nargs="+",
    help="add specific host templates"
)
opt_group.add_argument(
    "-c",
    "--clear",
    nargs="+",
    help="del specific host templates"
)
opt_group.add_argument(
    "-u",
    "--use",
    nargs="+",
    help="use specific host templates"
)
opt_group.add_argument(
    "-r",
    "--replace",
    nargs="+",
    help="replaced specific host templates"
)
parser.set_defaults(handler=main)
