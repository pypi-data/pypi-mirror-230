#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Gary
# Datetime: 2022/12/19 16:48
# IDE: PyCharm
import convertapi
import logging
import hashlib
import configparser
import re
import numpy
import pandas
import jmespath
import time
import traceback
import sys
import json
import os
import IPy
from bisect import bisect_left
from convertapi import ApiError, BaseError
from datetime import datetime
from dateutil.parser import parse
from prettytable import PrettyTable
from openpyxl.utils import get_column_letter
from diskcache import Cache


class IPS:
    def __init__(self, check_file):
        self.check_file = check_file

    @property
    def idc_networks(self):
        """
            读取 ip_range.json 中的机房网段信息：
        :return:
        """
        IDC_NETWORKS = []
        if self.check_file and os.path.exists(self.check_file):
            with open(self.check_file, mode="r", encoding="utf8") as fp:
                for value in json.load(fp).values():
                    IDC_NETWORKS.extend([IPy.IP(net) for net in value])
            return IDC_NETWORKS

    def valid_ip(self, ip: str):
        """
            验证 ip 是否在机房网段内：
        :param ip:
        :return:
        """
        if ip and self.idc_networks:
            for net in self.idc_networks:
                if ip in net:
                    return True
        return False


def make_timestamp(date: str):
    """
        将输入的字符串格式的日期转化为时间戳：
            1. date 的格式可以是多种，如：2023-01-10、20230110、2023/01/10 等。
    :param date:
    :return:
    """
    return time.mktime(
        time.strptime(
            datetime.strftime(
                parse(date),
                "%Y%m%d"
            ),
            "%Y%m%d"
        )
    )


def convert_unit(size):
    """
        1. 通过二分查找法将 bytes 转换为易读的单位：
    :param size:
    :return:
    """
    factor = bisect_left(
        [1024 ** i for i in range(1, 8)],
        size
    )
    return str(round(size / (1024 ** factor), 2)) + "BKMGTPE"[factor]


def convert_pdf(api_secret: str, output_docx: str):
    """
        将 Word 文档转化为 PDF 文档：
    :param api_secret:
    :param output_docx:
    :return:
    """
    try:
        if api_secret:
            convertapi.api_secret = api_secret
            res = convertapi.convert("pdf", {"File": output_docx})
            res.file.save(output_docx.replace(".docx", ".pdf"))
            logging.info(
                "\033[32mPDF 报表导出完成： %s\033[0m",
                os.path.abspath(output_docx) if os.path.exists(output_docx) else ""
            )
    except (ApiError, BaseError):
        logging.error(traceback.format_exc())
        sys.exit(-1)


class DiskCache:
    def __init__(self):
        self._cache = Cache(
            get_value(
                section="CACHE",
                option="CACHE_FILE"
            )
        )

    def set_cache(self, key, value, expire=None, retry=True):
        """
            设置本地文件缓存：
        :param key:
        :param value:
        :param expire:
        :param retry:
        :return:
        """
        self._cache.set(
            key=key,
            value=value,
            expire=expire,
            retry=retry
        )

    def get_cache(self, key) -> str:
        """
            读取本地文件缓存：
        :param key:
        :return:
        """
        return self._cache.get(key=key)


def get_value(section: str, option: str, raw: bool = False) -> str:
    """
        读取 configs.ini 配置文件中的参数信息：
            1. configs.ini 配置文件中以 section 作为分类，section 区分大小写；
            2. section 由 option 组成(类似于 "k = v")，option 不区分大小写；
            3. option 中的 value 可以包含占位符，但在读取时必须指定 "raw=True" 参数，否则将被作为变量处理。
    :param section:
    :param option:
    :param raw:
    :return:
    """
    configs = configparser.ConfigParser()
    configs.read(
        filenames=os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "configs.ini"
        ),
        encoding="utf-8"
    )
    return configs.get(
        section=section,
        option=option,
        raw=raw
    )


def pretty_tbl(title: str, field_names: list, rows: list):
    """
        实例化表格输出对象：
    :param title:
    :param field_names:
    :param rows:
    :return:
    """
    tbl = PrettyTable()
    tbl.title = title
    tbl.field_names = field_names
    tbl.add_rows(rows=rows)
    return tbl


def jmes_search(jmes_rexp: str, data: list or dict, options=None):
    """
        通过 Jmes 处理 Json 字符串：
    :param jmes_rexp:
    :param data:
    :param options:
    :return:
    """
    try:
        return jmespath.search(
            expression=jmes_rexp,
            data=data,
            options=options
        )
    except Exception as err:
        logging.error(msg="\033[31m" + str(err) + "\033[0m")


def md5_(text: str) -> str:
    """
        生成 hash 信息摘要：
            1. 采用 md5 加密算法；
            2. 为支持中文，需要编码为 utf-8。
    :param text: 要加密的字符串
    :return:
    """
    md5 = hashlib.md5()
    if text:
        md5.update(text.encode("utf-8"))
        return md5.hexdigest()


def re_search(rexp: str, content: str, mode=re.X) -> bool:
    """
        正则表达式搜索字符串：
    :param rexp:
    :param content:
    :param mode:
    :return:
    """
    return bool(re.compile(rexp, mode).search(content))


def re_findall(rexp: str, content: str, mode=re.X) -> list:
    """
        正则表达式匹配所有符合条件的字符串：
    :param rexp:
    :param content:
    :param mode:
    :return:
    """
    return re.compile(rexp, mode).findall(content)


def re_sub(rexp: str, replaced_str: str, origin_str: str) -> str:
    """
        正则表达式查找字符串并替换：
    :param rexp:
    :param replaced_str:
    :param origin_str:
    :return:
    """
    return re.compile(rexp).sub(replaced_str, origin_str)


def to_excel_(df: pandas.DataFrame, fname: str, shname: str = "Sheet1"):
    """
        利用 Pandas、Numpy 自动设置单元格列宽并导出为 Execl 文件：
            1. 如果要操作 "xlsx" 格式的文件，需要将 ExcelWriter 的引擎设置为 "openpyxl"；
            2. with 语句会自动保存文件。
    :param df: Pandas DataFrame
    :param fname: Execl Filename
    :param shname: Execl Sheet Name
    :return:
    """
    widths = numpy.max(
        [
            # 计算每列表头的字符宽度
            df.columns.to_series().apply(lambda x: len(x.encode("utf-8"))).values,
            # 计算每列的最大字符宽度
            df.astype(str).applymap(lambda x: len(x.encode("utf-8"))).agg(max).values
        ],
        axis=0
    )
    with pandas.ExcelWriter(
            fname,
            engine=get_value(section="EXCEL", option="PANDAS_WRITE_EXCEL_ENGINE")
    ) as writer:
        df.to_excel(excel_writer=writer, sheet_name=shname, index=False)
        for i, width in enumerate(widths, start=1):
            writer.sheets[shname].column_dimensions[get_column_letter(i)].width = width + 2
