#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Gary
# Datetime: 2022/12/20 13:26
# IDE: PyCharm
import logging
import ldap3
from .format import get_value, jmes_search


class Ldap:
    def __init__(self, host: str, user: str, passwd: str, port=389):
        self.__host = host
        self.__user = user
        self.__passwd = passwd
        self.__port = port

    @property
    def host(self):
        if self.__host:
            return self.__host

    @property
    def user(self):
        if self.__user:
            return self.__user

    @property
    def passwd(self):
        if self.__passwd:
            return self.__passwd

    @property
    def port(self):
        if self.__port:
            return self.__port

    def login(self):
        """
            建立 LDAP 远程客户端连接：
        :return:
        """
        try:
            return ldap3.Connection(
                server=ldap3.Server(
                    host=self.host,
                    port=self.port
                ),
                user=self.user,
                password=self.passwd,
                auto_bind=True
            )
        except Exception as err:
            logging.error(msg="\033[31m" + str(err) + "\033[0m")

    def search_user(self, dn, filter_, results="raw_dn",
                    search_scope=ldap3.SUBTREE, attributes=ldap3.ALL_ATTRIBUTES):
        """
            搜索 LDAP 用户信息：
        :param dn:
        :param filter_:
        :param results:
        :param search_scope:
        :param attributes:
        :return:
        """
        client = self.login()
        if dn:
            # res 只返回真假的 bool 值
            res = client.search(
                search_base=dn,
                search_scope=search_scope,
                search_filter=filter_,
                attributes=attributes
            )
            if client.response:
                return client.response[0].get(results) if res else None

    def search_usergrp(self, dn, filter_="(cn=*)", attributes=ldap3.NO_ATTRIBUTES):
        """
            搜索 LDAP 用户组信息：
        :param dn:
        :param filter_:
        :param attributes:
        :return:
        """
        client = self.login()
        res = client.search(
            search_base=dn,
            search_scope=ldap3.SUBTREE,
            search_filter=filter_,
            attributes=attributes
        )
        if res:
            return jmes_search(
                jmes_rexp=get_value(section="JMES", option="SEARCH_LDAP_CN"),
                data=client.response
            )

    def clean_usergrp(self, dn):
        """
            清除 LDAP 用户组：
        :param dn:
        :return:
        """
        if self.search_usergrp(dn=dn):
            for usergrp in self.search_usergrp(dn):
                try:
                    self.login().delete(usergrp)
                    logging.info("\033[32m成功清除LDAP用户组 '%s'\033[0m", usergrp)
                except Exception as err:
                    logging.error(msg="\033[31m" + str(err) + "\033[0m")

    def create_usergrp(self, dn, member: list):
        """
            创建 LDAP 用户组：
        :param dn:
        :param member:
        :return:
        """
        try:
            self.login().add(dn, "groupOfUniqueNames")
            if member:
                self.update_member(dn, member)
        except Exception as err:
            logging.error(msg="\033[31m" + str(err) + "\033[0m")

    def update_member(self, cn, member: list = None):
        """
            更新 LDAP 用户组成员信息：
        :param cn:
        :param member:
        :return:
        """
        try:
            if member:
                self.login().modify(
                    cn,
                    {"uniqueMember": [(ldap3.MODIFY_REPLACE, member)]}
                )
        except Exception as err:
            logging.error(msg="\033[31m" + str(err) + "\033[0m")
