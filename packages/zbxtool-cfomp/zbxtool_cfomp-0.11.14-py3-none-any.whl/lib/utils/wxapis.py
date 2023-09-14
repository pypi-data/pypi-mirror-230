#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Gary
# Datetime: 2022/12/20 21:31
# IDE: PyCharm
import logging
import sys
from weworkapi.CorpApi import CORP_API_TYPE, CorpApi
from weworkapi.AbstractApi import ApiException
from .format import jmes_search, DiskCache, get_value


class WxWorkApi:
    def __init__(self, corpid: str, agentid: str, secret: str):
        # 企业 id
        self.__corpid = corpid
        # 应用 id
        self.__agentid = agentid
        # 应用 secret
        self.__secret = secret
        self._corpapi = CorpApi(self.__corpid, self.__secret)

    @property
    def corpid(self):
        """readonly"""
        return self.__corpid

    @property
    def secret(self):
        """readonly"""
        return self.__secret

    @property
    def token(self):
        """
            Get token, expire time is 7100s
                1. 每个应用有独立的 secret，获取到的 access_token 只能本应用使用；
                2. 每个应用的 access_token 应该分开来获取。
        :return:
        """
        instance_ = DiskCache()
        if self.__agentid:
            key = "token_" + str(self.__corpid) + "_" + str(self.__agentid)
            if instance_.get_cache(key):
                return instance_.get_cache(key)
            if self.secret:
                try:
                    instance_.set_cache(
                        key=key,
                        value=self._corpapi.getAccessToken(),
                        expire=int(
                            get_value(
                                section="CACHE",
                                option="TOKEN_EXPIRE_TIME"
                            )
                        )
                    )
                except ApiException as err:
                    logging.error(msg="\033[31m" + str(err) + "\033[0m")
                else:
                    return instance_.get_cache(key)

    def _wework_request(self, api_type: str, params=None):
        """
            封装对corpapi的调用
        """
        try:
            if self.token:
                self._corpapi.access_token = self.token
                return self._corpapi.httpCall(api_type, params)
        except ApiException as err:
            logging.error(msg="\033[31m" + str(err) + "\033[0m")
            sys.exit(1)

    @property
    def departs(self):
        """
            获取企业微信中所有的部门信息：
        :return:
        """
        return self._wework_request(
            api_type=CORP_API_TYPE["DEPARTMENT_LIST"]
        )

    def get_depid(self, dep_name: str):
        """
            根据部门名称获取部门 id：
        :param dep_name:
        :return:
        """
        if self.departs:
            depid = jmes_search(
                jmes_rexp=get_value(
                    section="JMES",
                    option="SEARCH_WEWORK_DEP_NAME",
                    raw=True
                ) % dep_name,
                data=self.departs.get("department")
            )
            return str(depid[0]) if depid else None

    def get_dep_users(self, dep_name: str):
        """
            根据部门名称获取其所有员工信息：
        :param dep_name:
        :return:
        """
        if not self.get_depid(dep_name):
            logging.error("\033[31m" + "企业微信中未找到部门: %s。" + "\033[0m", dep_name)
            sys.exit(1)
        users = self._wework_request(
            api_type=CORP_API_TYPE["USER_LIST"],
            params={
                "department_id": self.get_depid(dep_name),
                "fetch_child": "1"
            }
        )
        return users["userlist"] if users and users["userlist"] else None
