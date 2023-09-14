#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ssl
from ast import literal_eval
import pyVim.connect
import pyVmomi
from lib.utils.format import get_value, DiskCache
from infi.pyvmomi_wrapper.esxcli import EsxCLI


class VMManger:
    def __init__(self, host: str, user: str, passwd: str, port: int = 443):
        self._host = host
        self._user = user
        self._passwd = passwd
        self._port = port

    @property
    def content(self):
        """
            获取 vCenter Server 的 Content 信息：
                1. 建立连接时采用 SmartConnect() 方法，由于版本原因，某些版本中没有 SmartConnectNoSSL() 方法；
                2. 建立连接时为避免证书认证，使用 ssl 模块跳过远程证书认证。
        :return:
        """
        ssl_context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
        ssl_context.verify_mode = ssl.CERT_NONE
        return pyVim.connect.SmartConnect(
            host=self._host,
            user=self._user,
            pwd=self._passwd,
            port=self._port,
            sslContext=ssl_context
        ).RetrieveContent()

    def get_objs(self, obj_type):
        """
            根据对象类型获取 vCenter Server 中所有对应的 View：
                1. 例如指定 pyVmomi.vim.Datacenter 类型获取所有的 DataCenter 对象；
                2. 例如指定 pyVmomi.vim.HostSystem 类型获取所有的 ESXI 主机对象。
        :param obj_type:
        :return:
        """
        return self.content.viewManager.CreateContainerView(
            self.content.rootFolder,
            [obj_type],
            True
        ).view

    def get_obj(self, obj_type, view_name: str):
        """
            根据对象类型和 view 名称获取指定 View：
        :param obj_type:
        :param view_name:
        :return:
        """
        for view in self.get_objs(obj_type):
            if view.name == view_name:
                return view

    def get_custom_fields(self, view, obj_type, key_: str, field_name: str):
        """
            获取 View 对象的自定义参数信息：
                1. view 类型可以是 DataCenter，也可以是 ESXI 主机，
                   在 vCenter Server 中，DataCenter、ESXI、Host 等都可以指定自定义参数；
                2. 获取到的 view 的所有自定义参数按照原有的格式写入字典；
                3. 最后根据自定义参数字典过滤机房和机柜信息。
        :param view:
        :param obj_type:
        :param key_:
        :param field_name:
        :return:
        """
        esxi_info = dict()
        props = dict()
        fields = dict()
        for prop in view.customValue:
            props[prop.key] = prop.value
        for field in self.content.customFieldsManager.field:
            if field.managedObjectType == obj_type:
                if field.key in props.keys():
                    fields[field.name] = props[field.key]
        if fields.get(field_name):
            esxi_info[key_] = fields.get(field_name)
            return esxi_info
        else:
            if key_ == "location":
                esxi_info[key_] = view.name
                return esxi_info
            if key_ == "site_rack":
                esxi_info[key_] = None
                return esxi_info

    def find_esxi(self, esxi_name: str):
        """
            遍历所有的 DataCenter 和 Compute Cluster 找到 ESXI 主机并获取其机房信息：
        :param esxi_name:
        :return:
        """
        for view in self.get_objs(pyVmomi.vim.Datacenter):
            for child in view.hostFolder.childEntity:
                if child.name == esxi_name:
                    return self.get_custom_fields(
                        view=view,
                        obj_type=pyVmomi.vim.Datacenter,
                        key_="location",
                        field_name="机房名称"
                    )
                if isinstance(child, pyVmomi.vim.ClusterComputeResource):
                    for host in child.host:
                        if host.name == esxi_name:
                            return self.get_custom_fields(
                                view=view,
                                obj_type=pyVmomi.vim.Datacenter,
                                key_="location",
                                field_name="机房名称"
                            )

    def fetch_esxi(self, esxi_name: str):
        """
            获取指定 ESXI 主机信息：
        :param esxi_name:
        :return:
        """
        instance_ = DiskCache()
        if instance_.get_cache("esxi_" + esxi_name):
            return instance_.get_cache("esxi_" + esxi_name)
        if not instance_.get_cache("esxi_" + esxi_name):
            esxi_ = self.get_obj(pyVmomi.vim.HostSystem, esxi_name)
            esxi_hardware = esxi_.summary.hardware if esxi_ else None
            esxi_info = self.find_esxi(esxi_name)
            if esxi_info:
                esxi_info["type"] = "Server"
                esxi_info["name"] = esxi_.name
                if esxi_.config:
                    esxi_info["os"] = esxi_.config.product.name
                    esxi_info["os_short"] = esxi_.config.product.osType
                esxi_info["os"] = "VMware ESXi"
                esxi_info["os_short"] = "vmnix-x86"
                esxi_info["os_full"] = esxi_.summary.config.product.fullName
                esxi_info["model"] = esxi_hardware.model
                esxi_info["vendor"] = esxi_hardware.vendor
                esxi_info["hardware_full"] = "\n".join(
                    [
                        get_value(section="VCENTER", option="VCENTER_CPU", raw=True) % (
                            esxi_hardware.cpuModel,
                            esxi_hardware.numCpuPkgs,
                            esxi_hardware.numCpuCores,
                            esxi_hardware.numCpuThreads
                        ),
                        f"内存: {esxi_hardware.memorySize / 1024 / 1024 // 1024}GB"
                    ]
                )
            # get host's ipA and netmask
            if esxi_ and esxi_.config:
                for vnic in esxi_.config.network.vnic:
                    if isinstance(vnic, pyVmomi.vim.host.VirtualNic):
                        esxi_info["host_networks"] = vnic.spec.ip.ipAddress
                        esxi_info["alias"] = vnic.spec.ip.ipAddress
                        esxi_info["host_netmask"] = vnic.spec.ip.subnetMask

            # get host's mac address
            if esxi_ and esxi_.config:
                for portgroup in esxi_.config.network.portgroup:
                    for port in portgroup.port:
                        if port.type == "host":
                            esxi_info["macaddress_a"] = "".join(port.mac)

            # get host's serial_number
            ordered_keys = literal_eval(
                get_value(
                    section="VCENTER",
                    option="HOST_SERIAL_ORDERED_KEY"
                )
            )
            sn_info = {}
            if esxi_hardware:
                for iden in esxi_hardware.otherIdentifyingInfo:
                    if isinstance(iden, pyVmomi.vim.host.SystemIdentificationInfo) \
                            and iden.identifierType.key in ordered_keys:
                        sn_info[iden.identifierType.key] = iden.identifierValue

            for key in ordered_keys:
                if sn_info.get(key):
                    esxi_info["serialno_a"] = sn_info.get(key)
                    break

            if esxi_info and esxi_info.get("serialno_a") == "None":
                esxi_info["serialno_a"] = EsxCLI(esxi_).get("hardware.platform").Get().SerialNumber

            if esxi_info:
                esxi_info.update(
                    self.get_custom_fields(
                        view=esxi_,
                        obj_type=pyVmomi.vim.HostSystem,
                        key_="site_rack",
                        field_name="机柜"
                    )
                )
            instance_.set_cache(
                key="esxi_" + esxi_name,
                value=esxi_info,
                expire=60
            )
            return instance_.get_cache("esxi_" + esxi_name)
