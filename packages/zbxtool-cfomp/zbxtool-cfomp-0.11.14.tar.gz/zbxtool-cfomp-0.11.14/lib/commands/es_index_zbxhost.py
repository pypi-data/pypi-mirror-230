#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    获取 Zabbix 主机 inventory 信息并生成 ES 索引。
"""
import argparse
import logging
import time
from datetime import datetime
from lib.utils.esapis import ESManager


def get_hosts(args, es_client, tpl_name):
    """
        获取 Zabbix 主机的 Inventory 信息：
    :param args:
    :param es_client:
    :param tpl_name:
    :return:
    """
    body_datas = []
    hosts = args.zapi.host.get(
        {
            "output": "extend",
            "selectGroups": "extend",
            "selectInterfaces": "extend",
            "selectInventory": "extend",
            "selectTags": "extend",
            "selectInheritedTags": "extend"
        }
    )
    localtime = time.strftime("%Y.%m.%d", time.localtime())
    for host in hosts:
        host["@timestamp"] = datetime.utcfromtimestamp(time.time())
        inventory = host.get("inventory") if isinstance(host.get("inventory"), dict) else {}
        body_datas.append(
            {
                "_id": host.get("hostid"),
                "主机名称": inventory.get("name", host.get("host")),
                "主机别名": inventory.get("alias", host.get("host")),
                "接口地址": [
                    interface.get("ip") for interface in host.get("interfaces")
                    if host.get("interfaces")
                ],
                "主机组": [
                    group.get("name") for group in host.get("groups")
                    if host.get("groups")
                ],
                "OS": inventory.get("os"),
                "OS_FULL": inventory.get("os_full"),
                "OS_SHORT": inventory.get("os_short"),
                "资产标签": inventory.get("asset_tag"),
                "主负责人": inventory.get("poc_1_name"),
                "次负责人": inventory.get("poc_2_name"),
                "机架": inventory.get("chassis"),
                "子网掩码": inventory.get("host_netmask"),
                "主机网络": inventory.get("host_networks"),
                "机房": inventory.get("location"),
                "机柜": inventory.get("site_rack"),
                "序列号": inventory.get("serialno_a"),
                "管理IP": inventory.get("oob_ip"),
                "MAC_A": inventory.get("macaddress_a"),
                "MAC_B": inventory.get("macaddress_b"),
                "硬件架构": inventory.get("hw_arch"),
                "标签": inventory.get("tag"),
                "类型": inventory.get("type"),
                "具体类型": inventory.get("type_full"),
                "型号": inventory.get("model"),
                "供应商": inventory.get("vendor"),
                "主机标签名称": [tag.get("tag") for tag in host.get("tags") if host.get("tags")],
                "主机标签值": [tag.get("value") for tag in host.get("tags") if host.get("tags")],
                "继承标签名称": [
                    tag.get("tag") for tag in host.get("inheritedTags")
                    if host.get("inheritedTags")
                ],
                "继承标签值": [
                    tag.get("value") for tag in host.get("inheritedTags")
                    if host.get("inheritedTags")
                ],
                "@timestamp": datetime.utcfromtimestamp(time.time())
            }
        )
    es_client.put_template(tpl_name=tpl_name)
    for host in hosts:
        host["_id"] = host["hostid"]
    index_of_raw_host = "zabbix-raw-host-info-" + localtime
    es_client.bulk(actions=hosts, index=index_of_raw_host)
    logging.info(
        "\033[32m成功生成 ES 索引：'(ES Host)%s' => '(ES INDEX)%s'\033[0m",
        args.es_url,
        index_of_raw_host
    )
    index_of_host = "zabbix-host-info-" + localtime
    es_client.bulk(actions=body_datas, index=index_of_host)
    logging.info(
        "\033[32m成功生成 ES 索引：'(ES Host)%s' => '(ES INDEX)%s'\033[0m",
        args.es_url,
        index_of_host
    )


def main(args):
    """创建 ES 索引"""
    get_hosts(
        args=args,
        es_client=ESManager(args.es_url, args.es_user, args.es_passwd),
        tpl_name=args.es_tpl
    )


parser = argparse.ArgumentParser(description="Gather zabbix host informations and create es index")
parser.add_argument(
    "--es_url",
    type=str,
    required=True,
    help="ElasticSearch server ip"
)
parser.add_argument(
    "--es_user",
    default="",
    help="ElasticSearch server login user"
)
parser.add_argument(
    "--es_passwd",
    default="",
    help="ElasticSearch server login password"
)
parser.add_argument(
    "--es_tpl",
    required=True,
    help="ElasticSearch index template name"
)
parser.set_defaults(handler=main)
