#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Gary
# Datetime: 2022/12/2 16:05
# IDE: PyCharm
import logging
import sys
import multicommand
from zabbix_api import ZabbixAPI
from lib import commands


def main():
    parser = multicommand.create_parser(commands)
    parser.add_argument(
        "-s", "--zbx-server",
        required=True,
        type=str,
        help="URL of zabbix server"
    )
    parser.add_argument(
        "-u", "--zbx-user",
        required=True,
        type=str,
        help="Zabbix server login username"
    )
    parser.add_argument(
        "-p", "--zbx-passwd",
        required=True,
        type=str,
        help="Zabbix server login password"
    )
    parser.add_argument(
        "-t", "--timeout",
        default=60,
        type=int,
        help="Zabbix API timeout"
    )
    parser.add_argument(
        "-l", "--level",
        choices=["CRITICAL", "FATAL", "ERROR", "WARN", "INFO", "DEBUG"],
        default="INFO",
        type=str,
        help="Logging level"
    )
    args = parser.parse_args()
    # 设置默认日志级别：getattr(logging, args.level) 返回的是日志级别对应的数值(int)
    logging.basicConfig(level=getattr(logging, args.level))
    zapi = ZabbixAPI(server=args.zbx_server, timeout=args.timeout)
    zapi.validate_certs = False
    zapi.login(user=args.zbx_user, password=args.zbx_passwd)
    setattr(args, "zapi", zapi)
    if hasattr(args, "handler"):
        args.handler(args)
    zapi.logout()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(1)
