#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Gary
# Datetime: 2022/12/19 20:39
# IDE: PyCharm
"""
    从企业微信中获取用户 ID，更新到 zabbix 用户的企业微信告警媒介的 sendto。
"""
import argparse
import sys
import os
from functools import reduce
import logging
import copy
from ast import literal_eval
from lib.utils.zbxapis import ZabbixApiUpdate
from lib.utils.format import pretty_tbl, get_value, jmes_search
from lib.utils.wxapis import WxWorkApi


def show(zbx_users: list):
    """
        打印出配置有企业微信告警媒介的用户信息：
    :param zbx_users:
    :return:
    """
    tbl = pretty_tbl(
        title="Zabbix用户企业微信账号对照",
        field_names=["Zabbix Userid", "Zabbix User Fullname", "Zabbix User Sendto"],
        rows=[
            [
                zbx_user.get("username"),
                zbx_user.get("fullname") if zbx_user.get("fullname") else "",
                zbx_user.get("output_sendto") if zbx_user.get("output_sendto") else ""
            ]
            for zbx_user in zbx_users
            if zbx_users
        ]
    )
    tbl.align["Zabbix Userid"] = "l"
    tbl.align["Zabbix User Fullname"] = "l"
    tbl.align["Zabbix User Sendto"] = "l"
    print(tbl)


class SyncWeworkMedia:
    def __init__(self, zapi, corpid, agentid, secret, depart_name,
                 zbx_usrgrps, zbx_username, extra_media_type):
        self._zapi = ZabbixApiUpdate(zapi)
        self._corpid = corpid
        self._agentid = agentid
        self._secret = secret
        self._zbx_usrgrps = zbx_usrgrps
        self._depart_name = depart_name
        self._zbx_username = zbx_username
        self._extra_media_type = extra_media_type

    def get_media_attr(self, media_type_name: str, attr: str):
        """
            获取指定的用户告警媒介信息：
        :param media_type_name:
        :param attr:
        :return:
        """
        media_type_id = jmes_search(
            jmes_rexp=get_value(
                section="JMES",
                option="SEARCH_MEDIATYPE_ID",
                raw=True
            ) % media_type_name,
            data=self._zapi.get_medias(output=["name"])
        )
        return {media_type_id: attr}

    @property
    def media_attrs(self):
        """
            获取用户告警媒介的指定信息：
        :return:
        """
        media_attrs = {}
        wework_media_type_ids = []
        for item in literal_eval(get_value(section="ZABBIX", option="MediaAttrList")):
            media_attr = self.get_media_attr(
                media_type_name=item.get("media_type_name"),
                attr=item.get("attr")
            )
            media_attrs.update(media_attr)
            if item["kind"] == "wework" and \
                    item.get("media_type_name") == self._extra_media_type:
                wework_media_type_ids.extend(list(media_attr.keys()))
        return media_attrs, wework_media_type_ids[0] if wework_media_type_ids else ""

    @property
    def zbx_users(self):
        """
            获取指定的用户信息：
        :return:
        """
        zbx_users = self._zapi.get_zbx_users(
            output=["alias", "name", "surname"],
            usrgrpids=jmes_search(
                jmes_rexp=get_value(
                    section="JMES",
                    option="SEARCH_USERGROUP_IDS"
                ),
                data=self._zapi.get_usr_grps(
                    filter_={"name": self._zbx_usrgrps},
                    output=["name"]
                )
            ),
            filter_={"username": self._zbx_username},
            selectmedias=["mediatypeid", "sendto", "active", "severity", "period"],
            selectmediatypes=["mediatypeid"]
        )
        for zbx_user in zbx_users:
            medias = zbx_user.get("medias")
            for media in medias:
                mediatypeid = media.get("mediatypeid")
                # {"1": "email", "5": "mobile", "12": "wework_id", "16": "wework_id"}
                if mediatypeid in self.media_attrs[0]:
                    attr = self.media_attrs[0].get(mediatypeid)
                    send = media.get("sendto")
                    sendto = send if isinstance(send, list) else [send]
                    if zbx_user.get(attr):
                        zbx_user[attr] += sendto
                    else:
                        zbx_user[attr] = sendto
            zbx_user["medias"] = medias
            del zbx_user["mediatypes"]
        return zbx_users

    def match_wework_userid(self, zbx_user: dict):
        """
           1. 从 zabbix 用户告警媒介中，通过报警媒介类型, 提取到用户的手机号码、邮箱、姓名等信息；
           2. 通过多种途径匹配到该用户在企业微信的 userid；
           3. 优先通过手机号码匹配, 如用户无手机号码或手机号码匹配不到，再依次通过其他途径匹配；
           4. 最终匹配到企业微信的 userid 的用户, 新建或更新报警媒介。
        :param zbx_user:
        :return:
        """
        match_funcs = [
            # 通过手机号码匹配
            lambda z_user, w_user: w_user.get("mobile") in z_user.get("mobile", []),
            # 通过 surname + name 匹配
            lambda z_user, w_user: z_user.get("fullname") == w_user.get("name"),
            # 通过 name + surname 匹配
            lambda z_user, w_user: z_user.get("fullname_reverse") == w_user.get("name"),
            # 通过邮箱匹配
            lambda z_user, w_user: w_user.get("email") in z_user.get("email", [])
        ]
        wework_users = WxWorkApi(
            corpid=self._corpid,
            agentid=self._agentid,
            secret=self._secret
        ).get_dep_users(self._depart_name)
        for match_func in match_funcs:
            result = [
                user
                for user in wework_users
                if wework_users and match_func(zbx_user, user)
            ]
            if result:
                return result[0].get("userid")

    def add_user_wework_media(self, zbx_user: dict, update=False, prefix=False):
        """
            为 zabbix 用户添加企业微信告警媒介。
            update: 如用户已经存在企业微信告警媒介, 且原 userid 与获取到的 userid 不一致,
                    值为 False 则不做处理，
                    值为 True 则更新为获取到的 userid。
        """
        wework_userid = self.match_wework_userid(zbx_user)
        if not wework_userid:
            logging.info(
                "\033[33m同步失败: Zabbix user '%s' 未找到对应的企业微信账号\033[0m",
                zbx_user.get("username")
            )
            return
        zbx_user_medias = zbx_user.get("medias")
        zbx_user_medias_copy = copy.deepcopy(zbx_user.get("medias"))
        sendto = f"{self._corpid}_{wework_userid}" if prefix else wework_userid
        add_media = {
            "mediatypeid": "",
            "sendto": sendto,
            "active": get_value(section="WEWORK", option="WEWORK_ACTIVE"),
            "severity": str(
                sum(literal_eval(get_value(section="WEWORK", option="WEWORK_SEVERITY")))
            ),
            "period": get_value(section="WEWORK", option="WEWORK_PERIOD")
        }
        # zabbix user 已经有 wework 报警媒介
        typeid = self.media_attrs[1]
        wework_media = jmes_search(
            jmes_rexp=get_value(
                section="JMES",
                option="SEARCH_WEWORK_MEDIA",
                raw=True
            ) % typeid,
            data=zbx_user_medias
        )
        # [{"mediatypeid": "", "sendto": "", "active": "", "severity": "", "period": ""}]
        if wework_media and not jmes_search(
                jmes_rexp=get_value(section="JMES", option="SEARCH_WEWORK_SENDTO", raw=True) % sendto,
                data=wework_media
        ):
            for media in wework_media:
                sendto = media.get("sendto")
                add_media.update({"mediatypeid": typeid})
                zbx_user_medias.append(add_media)
                # 企业微信 id 和企业微信用户 id 使用 "_" 进行分割，但是考虑到用户 id 中带有 "_" 的情况，
                # 因而指定分割次数，即 "maxsplit=1"
                wework_split = sendto.split("_", maxsplit=1)
                # 当 zabbix user 已经有了相应的 wework 告警媒介，但是此用户属于另一个企业时，需要再次添加
                # 考虑到企业微信用户名称中可能带有 "_" 的情况，"maxsplit=1" 指定根据匹配到的第一个 "_" 进行分割
                if sendto and len(wework_split) == 2 and wework_split[0] != self._corpid and prefix:
                    add_media.update({"mediatypeid": typeid})
                    zbx_user_medias.append(add_media)
                if update and sendto:
                    media.update(
                        {
                            "sendto": f"{wework_split[0]}_{wework_userid}" if
                            sendto and len(wework_split) == 2 else wework_userid
                        }
                    )
                    logging.info(
                        "\033[32m成功更新企业微信userid：Zabbix userid => '%s', "
                        "WeWork userid => '%s'\033[0m",
                        zbx_user.get("username"),
                        wework_userid
                    )
        if not wework_media:
            add_media.update({"mediatypeid": typeid})
            zbx_user_medias.append(add_media)
        # 对要更新的用户 medias 列表进行去重，防止重复添加
        distinct_zbx_user_medias = []
        if zbx_user_medias:
            for media in zbx_user_medias:
                if media not in distinct_zbx_user_medias:
                    distinct_zbx_user_medias.append(media)
        if distinct_zbx_user_medias != zbx_user_medias_copy:
            self._zapi.update_user(
                {
                    "userid": zbx_user.get("userid"),
                    "medias": distinct_zbx_user_medias
                }
            )
            logging.info(
                "\033[32m同步成功: Zabbix user: '%s', WeWork userid: '%s'\033[0m",
                zbx_user.get("username"),
                wework_userid
            )
        return add_media.get("sendto")


def main(args):
    """
    :param args:
    :return:
    """
    corpid = args.corpid
    secret = args.secret
    agentid = args.agentid
    if args.env:
        corpid = corpid if corpid else os.environ.get("WEWORK_CORPID")
        secret = secret if secret else os.environ.get("WEWORK_SECRET")
        agentid = agentid if agentid else os.environ.get("WEWORK_AGENTID")
    if corpid and secret and agentid:
        worker = SyncWeworkMedia(
            zapi=args.zapi,
            corpid=corpid,
            agentid=agentid,
            secret=secret,
            depart_name=args.depart_name,
            zbx_usrgrps=reduce(lambda x, y: x + y, args.usergroups) if args.usergroups else [],
            zbx_username=args.username,
            extra_media_type=args.media_type
        )
        zbx_users = worker.zbx_users
        for user in zbx_users:
            sendto = worker.add_user_wework_media(
                zbx_user=user,
                update=args.allow_update,
                prefix=args.allow_prefix
            )
            user["output_sendto"] = sendto
        show(zbx_users)
    else:
        parser.print_help()
        logging.error("\033[31m缺乏必要参数：'corpid' or 'secret' or 'agentid'\033[0m")
        sys.exit(1)


parser = argparse.ArgumentParser()
parser.add_argument("-c", "--corpid", required=True, help="企业微信的企业ID")
parser.add_argument("-t", "--secret", required=True, help="企业微信内应用的Secret")
parser.add_argument("-a", "--agentid", required=True, help="企业微信内应用的ID")
parser.add_argument("-d", "--depart_name", required=True, help="指定企业微信中部门名称")
parser.add_argument("-e", "--env", action="store_true", help="从环境变量中读取参数")
parser.add_argument("-g", "--usergroups", nargs="+", action="append", help="指定更新的zabbix用户组")
parser.add_argument("-u", "--username", help="指定更新的zabbix用户")
parser.add_argument("-m", "--media_type", required=True, help="指定zabbix中企业微信的告警媒介")
parser.add_argument("--allow-update", action="store_true", help="当zabbix user已存在企业微信告警媒介, \
但sendto字段与获取的企业微信userid不一致, 是否允许更新")
parser.add_argument("--allow-prefix", action="store_true", help="是否加上企业微信的企业id作为前缀，\
如'ww438e13e211d83d51_ChenHuiPing'")
parser.set_defaults(handler=main)
