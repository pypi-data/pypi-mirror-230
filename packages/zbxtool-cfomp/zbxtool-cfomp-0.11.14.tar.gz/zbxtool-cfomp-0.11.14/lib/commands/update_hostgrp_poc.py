#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    根据现有主机组负责人信息文件更新 Zabbix 主机组下所有主机的 Inventory POC 的负责人信息。
"""
import argparse
import json
import os
import logging
import ldap3
from lib.utils.ldapapis import Ldap


def get_hostgrp_users(zapi, exclude_groups):
    """
        查询所有以 "admins" 结尾的用户组的用户：
            1. 用户组和主机组有约定的对应关系，如主机组名为 "XYZ",则主机组对应的用户组为 "XYZ admins"；
            2. 由于 host inventory 中只能保存两个负责人信息（poc_1, poc_2），取用户组中的前两个用户。
    :param zapi:
    :param exclude_groups:
    :return:
    """
    grp_ldap_users = dict()
    non_users = list()
    usrgrps = zapi.usergroup.get(
        {
            "selectUsers": ["userid", "name", "surname"],
            "output": ["usrgrpid", "name"],
            "search": {"name": "* admins"},
            # If set to true enables the use of "*"
            # as a wildcard character in the search parameter
            "searchWildcardsEnabled": True
        }
    )
    if exclude_groups:
        non_poc_usrgrps = zapi.usergroup.get(
            {
                "selectUsers": ["userid", "name", "surname"],
                "output": ["usrgrpid", "name"],
                # 不是主机组负责人的内部用户或者特殊用户的用户组
                # "name" 的值不能为 None，否则是返回全部用户
                "filter": {"name": exclude_groups}
            }
        )
        if non_poc_usrgrps:
            for grp in non_poc_usrgrps:
                non_users += grp.get("users")
    for usrgrp in usrgrps:
        grp_name = usrgrp.get("name").rsplit(" ", maxsplit=1)[0]
        grp_ldap_users[grp_name] = {"GroupName": grp_name}
        users = [
            user for user in usrgrp.get("users") if user not in non_users
        ]
        for i in range(min(len(users), 2)):
            ldap_cn = f"{usrgrp.get('users')[i].get('name')} " \
                      f"{usrgrp.get('users')[i].get('surname')}"
            grp_ldap_users[grp_name][f"poc_{i + 1}_dn"] = \
                f"cn={ldap_cn},ou=Person,dc=shchinafortune,dc=local"
    return grp_ldap_users


def main(args):
    contacts = dict()
    ldap = Ldap(
        host=args.ldap_server,
        port=args.ldap_port,
        user=args.ldap_user,
        passwd=args.ldap_password
    )
    if os.path.exists(args.contacts_file):
        with open(file=args.contacts_file, mode="r", encoding="utf8") as f_obj:
            for info in json.load(f_obj)["HostGroup"]:
                contacts[info.get("GroupName")] = info
    htgrp_users = get_hostgrp_users(
        zapi=args.zapi,
        exclude_groups=args.exclude_usergroups
    )
    htgrp_users.update(contacts)
    htgrps = args.zapi.hostgroup.get(
        {
            "filter": {"name": list(htgrp_users.keys())},
            "output": ["groupid", "name"],
            "selectHosts": ["hostid"]
        }
    )
    for htgrp in htgrps:
        contact = htgrp_users.get(htgrp.get("name"), {})
        inventory = dict()
        for i in [1, 2]:
            ldap_dn = f"poc_{i}_dn"
            poc_info = ldap.search_user(
                dn=contact.get(ldap_dn),
                filter_="(objectClass=*)",
                search_scope=ldap3.BASE,
                results="attributes"
            )
            inventory[f"poc_{i}_name"] = \
                "".join(poc_info.get("sn", "") + poc_info.get("givenName", "")) if poc_info else ""
            inventory[f"poc_{i}_email"] = ",".join(poc_info.get("mail", "")) if poc_info else ""
            inventory[f"poc_{i}_phone_a"] = \
                poc_info.get("telephoneNumber", [""])[0] if poc_info else ""
            inventory[f"poc_{i}_phone_b"] = \
                poc_info.get("telephoneNumber", [""])[-1] if poc_info else ""
            inventory[f"poc_{i}_cell"] = ",".join(poc_info.get("mobile", "")) if poc_info else ""
            inventory[f"poc_{i}_screen"] = ",".join(poc_info.get("uid", "")) if poc_info else ""
        args.zapi.host.massupdate(
            {
                "hosts": htgrp.get("hosts"),
                "inventory_mode": 1,
                "inventory": inventory
            }
        )
        logging.info("\033[32m更新POC信息成功，主机组 -> '%s'\033[0m", htgrp.get("name"))


parser = argparse.ArgumentParser()
parser.add_argument("-c", "--contacts-file", required=True, help="HostGroup contacts file")
parser.add_argument("-l", "--ldap-server", required=True, help="ldap server ip address")
parser.add_argument("-o", "--ldap-port", default=389, help="ldap server port")
parser.add_argument("-u", "--ldap-user", required=True, help="ldap bind user")
parser.add_argument("-p", "--ldap-password", required=True, help="ldap password")
parser.add_argument("-e", "--exclude-usergroups", action="append", help="exclude usergroups")
parser.set_defaults(handler=main)
