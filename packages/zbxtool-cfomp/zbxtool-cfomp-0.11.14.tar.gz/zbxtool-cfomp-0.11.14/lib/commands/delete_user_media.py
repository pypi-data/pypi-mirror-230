#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import logging
from lib.utils.format import pretty_tbl


def show(zbx_users: list):
    tbl = pretty_tbl(
        title="Zabbix用户告警媒介对照",
        field_names=["Zabbix Userid", "Zabbix User Fullname", "Zabbix User Medias"],
        rows=[
            [
                zbx_user.get("username"),
                zbx_user.get("fullname") if zbx_user.get("fullname") else "",
                "/".join(zbx_user.get("medias"))
            ]
            for zbx_user in zbx_users
            if zbx_users
        ]
    )
    tbl.align["Zabbix Userid"] = "l"
    tbl.align["Zabbix User Fullname"] = "l"
    tbl.align["Zabbix User Medias"] = "l"
    print(tbl)


def delete_user_medias(zapi, medias: list):
    # 根据用户的输入的 media 列表直接通过 zabbix api 进行过滤
    medias = zapi.mediatype.get(
        {
            "output": ["name"],
            "filter": {"name": medias}
        }
    )
    mediatype_ids = [media.get("mediatypeid") for media in medias if medias]
    zbx_users = zapi.user.get(
        {
            "output": ["userid", "username"],
            "selectMedias": ["mediatypeid", "sendto", "active", "severity", "period"],
            "mediatypeids": mediatype_ids
        }
    )
    for user in zbx_users:
        zapi.user.update(
            {
                "userid": user.get("userid"),
                "medias": [
                    media for media in user.get("medias")
                    if media.get("mediatypeid") not in mediatype_ids
                ],
            }
        )
        logging.info(
            "\033[32m成功更新Zabbix用户medias：Zabbix userid => '%s'\033[0m",
            user.get("username")
        )


def main(args):
    zapi = args.zapi
    delete_user_medias(
        zapi=zapi,
        medias=args.media
    )
    zbx_users = zapi.user.get(
        {
            "output": ["userid", "alias", "name", "surname"],
            "selectMedias": ["mediatypeid"]
        }
    )
    for user in zbx_users:
        mediatype_ids = [
            media.get("mediatypeid")
            for media in user.get("medias") if user.get("medias")
        ]
        if mediatype_ids:
            mediatype_names = zapi.mediatype.get(
                {
                    "output": ["name"],
                    "filter": {"mediatypeid": mediatype_ids}
                }
            )
            user["medias"] = [name.get("name") for name in mediatype_names if mediatype_names]
    show(zbx_users=zbx_users)


parser = argparse.ArgumentParser(
    description="Delete the media types that user do not use"
)
parser.add_argument(
    "-m",
    "--media",
    required=True,
    type=str,
    nargs="+",
    help="user media type to delete"
)
parser.set_defaults(handler=main)
