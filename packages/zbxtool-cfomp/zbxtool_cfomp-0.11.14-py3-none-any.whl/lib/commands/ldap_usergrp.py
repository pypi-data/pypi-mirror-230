#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Gary
# Datetime: 2022/12/19 19:41
# IDE: PyCharm
"""
    主要用来处理 Zabbix 用户组和 LDAP 用户组：
        1. 根据 Zabbix 主机组创建用户组；
        2. 根据 Zabbix 用户组创建 LDAP 用户组；
        3. 清除 LDAP 用户组。
"""
import argparse
import logging
import sys
from lib.utils.ldapapis import Ldap
from lib.utils.format import get_value
from lib.utils.zbxapis import ZabbixApiCreate


class ZbxGrps:
    def __init__(self, zapi, ldap):
        self._zapi = ZabbixApiCreate(zapi)
        self._ldap = ldap

    @property
    def zbx_hostgrps(self):
        zbx_hostgrps = self._zapi.get_ht_grps(
            output=["name", "groupid"],
            filter_={"flags": 0},
            monitored_hosts=True
        )
        return zbx_hostgrps

    @property
    def zbx_usergrps(self):
        zbx_usergrps = self._zapi.get_usr_grps(
            searchwildcardsenabled=True,
            selectusers=["userid", "username", "name"],
            output=["username", "name"]
        )
        return zbx_usergrps

    def create_usrgrps_by_htgrps(self):
        usrgrps = [
            usergrp.get("name").replace(" admins", "")
            for usergrp in self.zbx_usergrps
        ]
        zbx_htgrps_without_usrgrp = list(
            filter(
                lambda grp: grp.get("name") not in usrgrps,
                self.zbx_hostgrps
            )
        )
        if zbx_htgrps_without_usrgrp:
            for htgrp in zbx_htgrps_without_usrgrp:
                self._zapi.create_usrgrp(
                    grp_name=htgrp.get("name") + " admins",
                    groupid=htgrp.get("groupid"),
                    # 3 - read-write access
                    permission=3
                )
                logging.info(
                    "\033[32m成功创建Zabbix用户组 '%s'\033[0m",
                    htgrp.get("name") + " admins"
                )

    def create_ldap_usrgrps(self):
        for zbx_grp in self.zbx_usergrps:
            unique_members = []
            # 判断 zabbix 用户是否存在于 ldap 中, 添加至成员列表
            for user in zbx_grp.get("users"):
                ldap_usr = self._ldap.search_user(
                    dn=get_value(section="LDAP", option="LDAP_USER_DN"),
                    filter_=f"(uid={user.get('username')})"
                )
                if ldap_usr:
                    unique_members.append(ldap_usr)
            # 特殊字符需进行处理
            zbx_grp_name = zbx_grp.get("name").replace("(", "\\28").replace(")", "\\29")
            ldap_usrgrp = self._ldap.search_usergrp(
                dn=get_value(section="LDAP", option="LDAP_USER_GROUP_DN"),
                filter_=f"(cn={zbx_grp_name})"
            )
            if ldap_usrgrp:
                self._ldap.update_member(ldap_usrgrp[0], unique_members)
                logging.info("\033[32m成功更新LDAP用户组 '%s'\033[0m", ldap_usrgrp[0])
            else:
                ldap_cn = f'cn={zbx_grp_name},' \
                          f'{get_value(section="LDAP", option="LDAP_USER_GROUP_DN")}'
                self._ldap.create_usergrp(dn=ldap_cn, member=unique_members)
                logging.info("\033[32m成功创建LDAP用户组 '%s'\033[0m", ldap_cn)


def main(args):
    ldap = Ldap(
        host=args.ldap_server,
        user=args.ldap_user,
        passwd=args.ldap_password,
        port=args.ldap_port
    )
    instance_ = ZbxGrps(args.zapi, ldap)
    # 创建 Zabbix 用户组
    if args.create_zbx_usrgrp:
        instance_.create_usrgrps_by_htgrps()

    # 清除 ldap 中 zabbix 用户组
    if args.clean:
        if not args.ldap_server or not args.ldap_user or not args.ldap_password:
            parser.print_help()
            logging.error("the argument --ldap-server/--ldap-user/--ldap-password is required")
            sys.exit(1)
        if args.ldap_server and args.ldap_user and args.ldap_password:
            ldap.clean_usergrp(dn=get_value(section="LDAP", option="LDAP_USER_GROUP_DN"))

    # 更新/新建 ldap group
    if args.create_ldap_group:
        if not args.ldap_server or not args.ldap_user or not args.ldap_password:
            parser.print_help()
            logging.error("the argument --ldap-server/--ldap-user/--ldap-password is required")
            sys.exit(1)
        if args.ldap_server or args.ldap_user or args.ldap_password:
            instance_.create_ldap_usrgrps()


parser = argparse.ArgumentParser()
parser.add_argument("--create-ldap-group", action="store_true")
parser.add_argument("--create-zbx-usrgrp", action="store_true")
parser.add_argument("-c", "--clean", action="store_true")
parser.add_argument("-s", "--ldap-server", help="ldap server ip address")
parser.add_argument("-o", "--ldap-port", default=389, help="ldap server port")
parser.add_argument("-u", "--ldap-user", help="ldap bind user")
parser.add_argument("-p", "--ldap-password", help="ldap password")
parser.set_defaults(handler=main)
