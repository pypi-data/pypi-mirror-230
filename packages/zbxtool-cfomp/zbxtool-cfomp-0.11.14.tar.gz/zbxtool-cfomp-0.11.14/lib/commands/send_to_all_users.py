#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Gary
# Datetime: 2022/12/8 16:05
# IDE: PyCharm
"""
    搜索用户配置的 Media 信息并自动将用户加入到对应 Action 的 send to users 列表。
"""
import argparse
import logging
from lib.utils.zbxapis import ZabbixApiUpdate


def update_action_send_users(zapi, media_name: str, action_name: str):
    """
        根据 Action 名称更新 operations 的 "send to users" 列表：
            1. 首先根据 Media 名称获取这个 Media 下的所有用户信息（即哪些用户配置了这个 Media）；
            2. 然后，根据 Action 名称获取 Operations 信息；
            3. 其次，获取此 Operation 原有的 "send to users" 列表；
            4. 再比对 "send to users" 列表和根据 Media 名称获取的用户列表；
            5. 最后追加不在原有 "send to users" 列表里的用户信息;
            6. 【action.update() 方法要求更新原有 Action 所有参数字段，否则会清空没有更新到的参数的值】。
    :param zapi:
    :param media_name:
    :param action_name:
    :return:
    """
    media = zapi.get_medias(
        filter_={"name": media_name},
        selectusers=["userid"],
        output=["users"]
    )
    action = zapi.get_actions(
        output="extend",
        selectoperations="extend",
        filter_={"name": action_name}
    )
    usr_groups = zapi.get_usr_grps(
        output=["usrgrpid", "name", "users"],
        selectusers=["userid"],
        filter_={"name": ["Zabbix administrators", "Disabled"]}
    )
    if not media or not action:
        logging.info("update None! Action -> ['%s']", action_name)
    if media and action:
        media_users = media[0].get("users")
        operations = action[0].get("operations")
        usrgrp_users = []
        for grp in usr_groups:
            usrgrp_users.extend(grp.get("users"))
        for operation in operations:
            # 排除在 "Zabbix administrators"、"Disabled" 这两个用户组中的用户
            media_users = [user for user in media_users if user not in usrgrp_users]
            ops_users = operation.get("opmessage_usr")
            ops_users.extend(media_users)
            # 对 "user_id" 进行去重
            new_ops_users = [dict(d) for d in (set([tuple(d.items()) for d in ops_users]))]
            operation["opmessage_usr"] = new_ops_users
            del operation["operationid"]
            del operation["actionid"]
            if not operation["opmessage"]["subject"]:
                del operation["opmessage"]["subject"]
            if not operation["opmessage"]["message"]:
                del operation["opmessage"]["message"]
        zapi.update_action(
            {
                "actionid": action[0].get("actionid"),
                "operations": operations
            }
        )
        logging.info(
            "\033[32m成功更新Action '%s'\033[0m",
            action[0].get("name")
        )


def main(args):
    """Main Function"""
    update_action_send_users(
        zapi=ZabbixApiUpdate(args.zapi),
        media_name=args.media,
        action_name=args.action
    )


parser = argparse.ArgumentParser(
    description="Automatically search for the media type configured by the user,"
                "and then configure it as action"
)
parser.add_argument(
    "-m",
    "--media",
    required=True,
    type=str,
    help="user configured media type"
)
parser.add_argument(
    "-a",
    "--action",
    required=True,
    type=str,
    help="the alarm action"
)
parser.set_defaults(handler=main)
