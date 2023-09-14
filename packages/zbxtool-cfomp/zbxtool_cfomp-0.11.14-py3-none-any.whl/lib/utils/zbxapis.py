#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Gary
# Datetime: 2022/12/19 14:33
# IDE: PyCharm
import logging
import sys
from zabbix_api import ZabbixAPIException
from .format import re_search, get_value


class ZabbixApiGet:
    """Zabbix Get Methods"""

    def __init__(self, zapi):
        self._zapi = zapi

    def _zbx_request(self, method: str, params: dict or list):
        """
            对于 zapi 的封装，等同于 zapi.MODULE.METHOD(PARAMS)。
        :param method:
        :param params:
        :return:
        """
        try:
            module, func = method.split(r".")
            return getattr(getattr(self._zapi, module), func)(params)
        except ZabbixAPIException as err:
            logging.error(msg="\033[31m" + str(err) + "\033[0m")
            sys.exit(1)

    def get_ht_grps(self, output=None, filter_=None, selecthosts=None,
                    monitored_hosts=True, real_hosts=False, with_monitored_items=False,
                    sortfield="name", **kwargs):
        """
            Get Zabbix host groups info:
        :param output: Object properties to be returned
        :param filter_: Return only those results that exactly match the given filter
        :param selecthosts: Return a hosts property with the hosts that belong to the host group
        :param monitored_hosts: Return only host groups that contain monitored hosts
        :param real_hosts: Return only host groups that contain hosts
        :param with_monitored_items: Return only host groups that contain hosts with enabled items
        :param sortfield: Sort the result by the given properties
        :param kwargs: Keyword parameters to merge
        :return:
        """
        default_dict = {
            "output": output,
            "filter": filter_,
            "selectHosts": selecthosts,
            "real_hosts": real_hosts,
            "with_monitored_items": with_monitored_items,
            "monitored_hosts": monitored_hosts,
            "sortfield": sortfield
        }
        default_dict.update(**kwargs)
        return self._zbx_request(
            method="hostgroup.get",
            params=default_dict
        )

    def get_hts(self, output=None, selectparenttemplates=None, selectinventory=None,
                searchinventory=None, selectgroups=None, selectinterfaces=None, filter_=None,
                hostids=None, searchbyany=False, groupids=None, selecttriggers=None,
                selectmacros=None, monitored_hosts=True, with_monitored_items=False,
                selecttags=None, search=None, tags=None, selecthostdiscovery=None, **kwargs):
        """
            Get Zabbix hosts info:
        :param selecthostdiscovery: Return a hostDiscovery property with host discovery object data
        :param tags: Return only hosts with given tags
                     Exact match by tag and case-sensitive or case-insensitive search by tag value
                     depending on operator value.
                     Format: [{"tag": "<tag>", "value": "<value>", "operator": "<operator>"}, ...]
        :param output: Object properties to be returned
        :param selectparenttemplates: Return a parentTemplates property with templates that the host is linked to
        :param selectinventory: Return an inventory property with host inventory data
        :param searchinventory: Return only hosts that have inventory data matching the given wildcard search
        :param selectgroups: Return a groups property with host groups data that the host belongs to
        :param selectinterfaces: Return an interfaces property with host interfaces
        :param filter_: Return only those results that exactly match the given filter
        :param hostids: Return only hosts with the given host IDs
        :param searchbyany: If set to true return results that match any of the criteria given in the filter or
                            search parameter instead of all of them
        :param groupids: Return only hosts that belong to the given groups
        :param selecttriggers: Return a triggers property with host triggers
        :param selectmacros: Return a macros property with host macros
        :param monitored_hosts: Return only monitored hosts
        :param with_monitored_items: Return only hosts that have enabled items
        :param selecttags: Return a tags property with host tags
        :param search: Return results that match the given wildcard search
        :param kwargs: Keyword parameters to merge
        :return:
        """
        default_dict = {
            "output": output,
            "selectParentTemplates": selectparenttemplates,
            "selectInventory": selectinventory,
            "searchInventory": searchinventory,
            "selectGroups": selectgroups,
            "selectInterfaces": selectinterfaces,
            "filter": filter_,
            "hostids": hostids,
            "searchByAny": searchbyany,
            "groupids": groupids,
            "selectTriggers": selecttriggers,
            "selectMacros": selectmacros,
            "monitored": monitored_hosts,
            "with_monitored_items": with_monitored_items,
            "selectTags": selecttags,
            "search": search,
            "tags": tags,
            "selectHostDiscovery": selecthostdiscovery
        }
        default_dict.update(**kwargs)
        return self._zbx_request(
            method="host.get",
            params=default_dict
        )

    def get_tpls(self, filter_=None, output=None, **kwargs):
        """
            Get Zabbix templates info:
        :param filter_: Return only those results that exactly match the given filter
        :param output: Object properties to be returned
        :param kwargs: Keyword parameters to merge
        :return:
        """
        default_dict = {
            "filter": filter_,
            "output": output
        }
        default_dict.update(**kwargs)
        return self._zbx_request(
            method="template.get",
            params=default_dict
        )

    def get_usr_grps(self, output=None, filter_=None, searchwildcardsenabled=False,
                     selectusers=None, search=None, **kwargs):
        """
            Get Zabbix user groups info:
        :param output: Object properties to be returned
        :param filter_: Return only those results that exactly match the given filter
        :param searchwildcardsenabled: If set to true enables the use of "*" as a wildcard character
                                       in the search parameter
        :param selectusers: Return the users from the user group in the users property
        :param search: Return results that match the given wildcard search (case-insensitive)
        :param kwargs: Keyword parameters to merge
        :return:
        """
        default_dict = {
            "output": output,
            "filter": filter_,
            "searchWildcardsEnabled": searchwildcardsenabled,
            "selectUsers": selectusers,
            "status": 0,
            "search": search
        }
        default_dict.update(**kwargs)
        return self._zbx_request(
            method="usergroup.get",
            params=default_dict
        )

    def get_zbx_users(self, output=None, usrgrpids=None, filter_=None,
                      selectmedias=None, selectmediatypes=None, **kwargs):
        """
            Get Zabbix users info:
        :param selectmediatypes: Return media types used by the user in the mediatypes property
        :param selectmedias: Return media used by the user in the medias property
        :param output: Object properties to be returned
        :param usrgrpids: Return only users that belong to the given user groups
        :param filter_: Return only those results that exactly match the given filter
        :param kwargs: Keyword parameters to merge
        :return:
        """
        default_dict = {
            "output": output,
            "usrgrpids": usrgrpids,
            "selectMedias": selectmedias,
            "selectMediatypes": selectmediatypes,
            "filter": filter_
        }
        default_dict.update(**kwargs)
        zbx_users = self._zbx_request(
            method="user.get",
            params=default_dict
        )
        for zbx_user in zbx_users:
            rexp = get_value(section="REXP", option="REXP_CH")
            if zbx_user.get("surname") and re_search(rexp, zbx_user.get("surname")) \
                    and zbx_user.get("name") and re_search(rexp, zbx_user.get("name")):
                # 添加 fullname 和 fullname_reverse，即 "姓+名" 和 "名+姓"（针对于中文名称）
                zbx_user["fullname"] = zbx_user.get("surname") + zbx_user.get("name")
                zbx_user["fullname_reverse"] = zbx_user.get("name") + zbx_user.get("surname")
        return zbx_users

    def get_drules(self, output=None, selectdchecks=None, search=None, selectdhosts=None,
                   searchwildcardsenabled=False, **kwargs):
        """
            Get Zabbix discovery rules info:
        :param selectdhosts: Return a dhosts property with the discovered hosts created by the discovery rule
        :param selectdchecks: Return a dchecks property with the discovery checks used by the discovery rule
        :param output: Object properties to be returned
        :param search: Return results that match the given wildcard search (case-insensitive)
        :param searchwildcardsenabled: If set to true enables the use of "*" as a wildcard character
                                       in the search parameter
        :param kwargs: Keyword parameters to merge
        :return:
        """
        default_dict = {
            "output": output,
            "selectDChecks": selectdchecks,
            "selectDHosts": selectdhosts,
            "search": search,
            "searchWildcardsEnabled": searchwildcardsenabled
        }
        default_dict.update(**kwargs)
        return self._zbx_request(
            method="drule.get",
            params=default_dict
        )

    def get_dservices(self, output=None, druleids=None, selectdrules=None,
                      selecthosts=None, **kwargs):
        """
            Get Zabbix discovery services info:
        :param output: Object properties to be returned
        :param druleids: Return only discovered services that have been detected by the given discovery rules
        :param selectdrules: Return a drules property with an array of the discovery rules that detected the service
        :param selecthosts: Return a hosts property with the hosts with the same IP address and proxy as the service
        :param kwargs: Keyword parameters to merge
        :return:
        """
        default_dict = {
            "output": output,
            "druleids": druleids,
            "selectDRules": selectdrules,
            "selectHosts": selecthosts,
        }
        default_dict.update(**kwargs)
        return self._zbx_request(
            method="dservice.get",
            params=default_dict
        )

    def get_items(self, hostids=None, search=None, filter_=None,
                  selectinterfaces=None, monitored=True, selecthosts=None, selecttags=None, **kwargs):
        """
            Get Zabbix items info:
        :param selecttags: Return the item tags in tags property
        :param hostids: Return only items that belong to the given hosts
        :param search: Return results that match the given wildcard search (case-insensitive)
        :param filter_: Return only those results that exactly match the given filter
        :param selectinterfaces: Return an interfaces property with an array of host interfaces used by the item
        :param monitored: If set to true return only enabled items that belong to monitored hosts
        :param selecthosts: Return a hosts property with an array of hosts that the item belongs to
        :param kwargs: Keyword parameters to merge
        :return:
        """
        default_dict = {
            "hostids": hostids,
            "search": search,
            "filter": filter_,
            "monitored": monitored,
            "selectInterfaces": selectinterfaces,
            "selectHosts": selecthosts,
            "selectTags": selecttags
        }
        default_dict.update(**kwargs)
        return self._zbx_request(
            method="item.get",
            params=default_dict
        )

    def get_medias(self, filter_=None, selectusers=None, output=None, **kwargs):
        """
            Get Zabbix media types info:
        :param filter_: Return only those results that exactly match the given filter
        :param selectusers: Return a users property with the users that use the media type
        :param output: Object properties to be returned
        :param kwargs: Keyword parameters to merge
        :return:
        """
        default_dict = {
            "filter": filter_,
            "selectUsers": selectusers,
            "output": output
        }
        default_dict.update(**kwargs)
        return self._zbx_request(
            method="mediatype.get",
            params=default_dict
        )

    def get_actions(self, output=None, selectoperations=None, filter_=None, **kwargs):
        """
            Get Zabbix actions info:
        :param output: Object properties to be returned
        :param selectoperations: Return an operations property with action operations
        :param filter_: Return only those results that exactly match the given filter
        :param kwargs: Keyword parameters to merge
        :return:
        """
        default_dict = {
            "output": output,
            "selectOperations": selectoperations,
            "filter": filter_
        }
        default_dict.update(**kwargs)
        return self._zbx_request(
            method="action.get",
            params=default_dict
        )

    def get_service(self, filter_=None, parentids=None, selectchildren=None,
                    selectparents=None, serviceids=None, **kwargs):
        """
            Get Zabbix services info:
        :param selectparents: Return a parents property with the parent services
        :param filter_: Return only those results that exactly match the given filter
        :param parentids: Return only services that are linked to the given parent services
        :param selectchildren: Return a children property with the child services
        :param serviceids: Return only services with the given IDs
        :param kwargs: Keyword parameters to merge
        :return:
        """
        default_dict = {
            "filter": filter_,
            "parentids": parentids,
            "selectParents": selectparents,
            "selectChildren": selectchildren,
            "serviceids": serviceids
        }
        default_dict.update(**kwargs)
        return self._zbx_request(
            method="service.get",
            params=default_dict
        )

    def get_events(self, output=None, countoutput=False, value=None, severities=None, time_from=None,
                   time_till=None, selecthosts=None, hostids=None, **kwargs):
        """
            Get Zabbix events info:
        :param output: Object properties to be returned
        :param countoutput: Return the number of records in the result instead of the actual data
        :param value: Return only events with the given values
        :param severities: Return only events with given event severities. Applies only if object is trigger
        :param time_from: Return only events that have been created after or at the given time
        :param time_till: Return only events that have been created before or at the given time
        :param selecthosts: Return a hosts property with hosts containing the object that created the event.
                            Supported only for events generated by triggers, items or LLD rules
        :param hostids: Return only events created by objects that belong to the given hosts
        :param kwargs: Keyword parameters to merge
        :return:
        """
        default_dict = {
            "output": output,
            "countOutput": countoutput,
            "value": value,
            "severities": severities,
            "time_from": time_from,
            "time_till": time_till,
            "selectHosts": selecthosts,
            "hostids": hostids,
        }
        default_dict.update(**kwargs)
        return self._zbx_request(
            method="event.get",
            params=default_dict
        )

    def get_trends(self, itemids=None, time_from=None, time_till=None, **kwargs):
        """
            Get Zabbix trends info:
        :param itemids: Return only trends with the given item IDs
        :param time_from: Return only values that have been collected after or at the given time
        :param time_till: Return only values that have been collected before or at the given time
        :param kwargs: Keyword parameters to merge
        :return:
        """
        default_dict = {
            "itemids": itemids,
            "time_from": time_from,
            "time_till": time_till
        }
        default_dict.update(**kwargs)
        return self._zbx_request(
            method="trend.get",
            params=default_dict
        )

    def get_sla(self, output=None, serviceids=None, selectservicetags=None, filter_=None, **kwargs):
        """
            Get Zabbix SLA info:
        :param output: Object properties to be returned
        :param serviceids: Return only SLAs matching the specific services
        :param selectservicetags: Return a service_tags property with SLA service tags
        :param filter_: Return only those results that exactly match the given filter
        :param kwargs: Keyword parameters to merge
        :return:
        """
        default_dict = {
            "output": output,
            "serviceids": serviceids,
            "selectServiceTags": selectservicetags,
            "filter": filter_
        }
        default_dict.update(**kwargs)
        return self._zbx_request(
            method="sla.get",
            params=default_dict
        )


class ZabbixApiUpdate(ZabbixApiGet):
    """Zabbix Update Methods"""

    def __init__(self, zapi):
        self._zapi = zapi
        super().__init__(zapi)

    def update_host(self, params: dict):
        """Update Zabbix host"""
        self._zbx_request(
            method="host.update",
            params=params
        )

    def update_user(self, params: dict):
        """Update Zabbix user"""
        self._zbx_request(
            method="user.update",
            params=params
        )

    def update_item(self, params: dict):
        """Update Zabbix item"""
        self._zbx_request(
            method="item.update",
            params=params
        )

    def update_action(self, params: dict):
        """Update Zabbix action"""
        self._zbx_request(
            method="action.update",
            params=params
        )

    def mass_update_host(self, params: dict):
        """Mass update Zabbix host"""
        self._zbx_request(
            method="host.massupdate",
            params=params
        )


class ZabbixApiCreate(ZabbixApiGet):
    """Zabbix Create Methods"""

    def __init__(self, zapi):
        self._zapi = zapi
        super().__init__(zapi)

    def create_item(self, delay=None, hostid=None, key_=None, name=None,
                    type_=None, value_type=None, data_type=None,
                    units=None, params=None, tags=None, **kwargs):
        """
            Create Zabbix item:
        :param tags: Item tags
        :param delay: Update interval of the item. Accepts seconds or a time unit with suffix (30s,1m,2h,1d)(required)
        :param hostid: ID of the host or template that the item belongs to(required)
        :param key_: Item key(required)
        :param name: Name of the item(required)
        :param type_: Type of the item(required)
        :param value_type: Type of information of the item(required)
        :param data_type:
        :param units: Value units
        :param params: Additional parameters depending on the type of the item
        :param kwargs: Keyword parameters to merge
        :return:
        """
        if tags is None:
            tags = []
        default_dt = {
            "delay": delay,
            "hostid": hostid,
            "key_": key_,
            "name": name,
            "type": type_,
            "value_type": value_type,
            "data_type": data_type,
            "units": units,
            "params": params,
            "tags": tags
        }
        default_dt.update(**kwargs)
        self._zbx_request(
            method="item.create",
            params=default_dt
        )

    def create_usrgrp(self, grp_name: str, groupid: str, permission: int):
        """
            Create Zabbix user group:
        :param grp_name: Name of the user group(required)
        :param groupid: ID of the host group to add permission to(required)
        :param permission: Access level to the host group(required)
                           0 - access denied
                           2 - read-only access
                           3 - read-write access
        :return:
        """
        self._zbx_request(
            method="usergroup.create",
            params={
                "name": grp_name,
                "rights": {
                    "id": groupid,
                    "permission": permission
                }
            }
        )

    def create_ht_interface(self, hostid: str, ip_: str, main: int = 0, port="10050", type_=1, useip=1):
        """
            Create Zabbix host interface:
        :param hostid: ID of the host the interface belongs to(required)
        :param ip_: IP address used by the interface(required)
        :param main: Whether the interface is used as default on the host.
                     Only one interface of some type can be set as default on a host
                        0 - not default
                        1 - default
        :param port: Port number used by the interface. Can contain user macros(required)
        :param type_: Interface type
                        1 - agent
                        2 - SNMP
                        3 - IPMI
                        4 - JMX
        :param useip: Whether the connection should be made via IP
                        0 - connect using host DNS name
                        1 - connect using host IP address for this host interface
        :return:
        """
        self._zbx_request(
            method="hostinterface.create",
            params={
                "hostid": hostid,
                "dns": "",
                "ip": ip_,
                "main": main,
                "port": port,
                "type": type_,
                "useip": useip
            }
        )

    def create_service(self, service_name: str, children=None, parents=None,
                       problem_tags=None, tags=None, algorithm: int = 1, sortorder: int = 0):
        """
            Create Zabbix service:
        :param tags: Service tags to be created for the service
        :param problem_tags: Problem tags to be created for the service
        :param parents: Parent services to be linked to the service
        :param children: Child services to replace the current service children
        :param sortorder: Position of the service used for sorting(required), Possible values: 0-999
        :param algorithm: Status calculation rule. Only applicable if child services exist(required)
                            0 - set status to OK
                            1 - most critical if all children have problems
                            2 - most critical of child services
        :param service_name: Name of the service(required)
        :return:
        """
        if tags is None:
            tags = list()
        if problem_tags is None:
            problem_tags = []
        if parents is None:
            parents = list()
        if children is None:
            children = list()
        return self._zbx_request(
            method="service.create",
            params={
                "name": service_name,
                "algorithm": algorithm,
                "sortorder": sortorder,
                "children": children,
                "parents": parents,
                "problem_tags": problem_tags,
                "tags": tags
            }
        )


class ZabbixApiDel(ZabbixApiGet):
    """Zabbix Delete Methods"""

    def __init__(self, zapi):
        self._zapi = zapi
        super().__init__(zapi)

    def del_service(self, serviceids: list):
        """Delete Zabbix service"""
        self._zbx_request(
            method="service.delete",
            params=serviceids
        )

    def del_interface(self, interfaceids: list):
        """Delete Zabbix host interface"""
        self._zbx_request(
            method="hostinterface.delete",
            params=interfaceids
        )
