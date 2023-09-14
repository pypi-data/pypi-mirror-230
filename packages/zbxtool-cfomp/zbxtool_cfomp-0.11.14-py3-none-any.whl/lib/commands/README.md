## zbxtool 6.0 各子命令功能介绍
* ```discovery```: 打印 Zabbix 自动发现主机信息, 或导出为 excel 文件。
* ```es_index_zbxhost```: 采集 Zabbix 中各主机的 inventory 信息并添加至 ElasticSearch 的 Index 中。
* ```fs_calc```: 在各 zabbix 主机上创建总磁盘空间和已用磁盘空间两个监控项。
* ```gen_analaysis_report```: 生成 zabbix 主机组资源使用率报表。
* ```hostgrp_aggr_item```: 在 Zabbix server 主机创建用于统计各主机组资源使用情况的监控项。
* ```hosttpl```: 批量添加、删除、更新 Zabbix 主机模板。
* ```inventory_supplementary```: vmware 主机更新 inventory type 字段为 vm, 主机有 rsync 进程监控项更新 host tag。
* ```ldap_usergrp```: 创建 Zabbix 每个主机组的用户组, 并同步到 ldap 的 ou=zabbix 的 user groups 中。
* ```multi_interfaces```: 输出 Zabbix 各主机的 inventory 的 Host networks 字段中的 ip 信息。
* ```oob```: 更新主机的 inventory OOB IP address 字段。
* ```send_to_all_users```: 按照 Media 类型自动将对应的用户添加到触发器动作的 send to users。
* ```service_tree```: 在 Zabbix 中依据主机组生成 it-service 树。
* ```sync_wework_media```: 从企业微信中获取用户 ID，更新到 Zabbix 用户的企业微信告警媒介的 sendto。
* ```update_hostgrp_poc```: 读取 ldap 人员信息, 更新 Zabbix 中各组主机的 inventory POC。
* ```update_hostname```: 消除 Zabbix 中 Discovered Hosts 组中 hostname 末尾的"下划线 + 数字"的情况。
* ```vmware_host_inventory```: 通过 Api 读取 vCenter 信息，更新 Zabbix 中 Hypervisors 组中 Host 的 inventory 信息。
* ```delete_user_media```: 删除用户不用的 mediatype
