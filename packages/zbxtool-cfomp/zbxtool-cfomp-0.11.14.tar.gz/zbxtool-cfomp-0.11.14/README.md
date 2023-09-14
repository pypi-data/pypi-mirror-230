# zbxtool

提供一些修改 zabbix 6.0 的操作。

## 使用说明
### 安装
* python setup.py install

### 查看帮助信息
```shell
# zbxtool -h
usage: zbxtool [-h] -s ZBX_SERVER -u ZBX_USER -p ZBX_PASSWD [-t TIMEOUT] [-l {CRITICAL,FATAL,ERROR,WARN,INFO,DEBUG}]
              [command] ...

optional arguments:
  -h, --help            show this help message and exit
  -s ZBX_SERVER, --zbx-server ZBX_SERVER
                        URL of zabbix server
  -u ZBX_USER, --zbx-user ZBX_USER
                        Zabbix server login username
  -p ZBX_PASSWD, --zbx-passwd ZBX_PASSWD
                        Zabbix server login password
  -t TIMEOUT, --timeout TIMEOUT
                        Zabbix API timeout
  -l {CRITICAL,FATAL,ERROR,WARN,INFO,DEBUG}, --level {CRITICAL,FATAL,ERROR,WARN,INFO,DEBUG}
                        Logging level

subcommands:

  [command]
    delete_user_media   Delete the media types that user do not use
    discovery           Get Zabbix 'Discovery' type host's info and ex ...
    es_index_zbxhost    Gather zabbix host informations and create es ...
    fs_calc
    gen_analaysis_report
    hostgrp_aggr_item
    hosttpl             (list|add|del) zabbix hosts templates
    inventory_supplementary
    ldap_usergrp
    multi_interfaces    find ip from host inventory
    oob                 Matching inventory OOB IP address
    send_to_all_users   Automatically search for the media type config ...
    service_tree        Create or delete zabbix service tree
    sync_wework_media
    update_hostgrp_poc
    update_hostname
    vmware_host_inventory
```

### 示例
- zbxtool -s 【URL】 -u 【USERNAME】 -p 【PASSWORD】 discovery -r "750-开发*" -o result.xlsx
- zbxtool -s 【URL】 -u 【USERNAME】 -p 【PASSWORD】 es_index_zbxhost --es_url 10.189.67.26 --es_user [ES_USER] --es_passwd [ES_PASSWD]
- zbxtool -s 【URL】 -u 【USERNAME】 -p 【PASSWORD】 fs_calc
- zbxtool -s 【URL】 -u 【USERNAME】 -p 【PASSWORD】 gen_analaysis_report -s 2022/12/01 -e 2022/12/31 -t 10
- zbxtool -s 【URL】 -u 【USERNAME】 -p 【PASSWORD】 gen_analaysis_report -s 2022/12/01 -e 2022/12/31 -t 10 -a [API_SECRET]
- zbxtool -s 【URL】 -u 【USERNAME】 -p 【PASSWORD】 hostgrp_aggr_item 运管平台
- zbxtool -s 【URL】 -u 【USERNAME】 -p 【PASSWORD】 hosttpl --hosts "Zabbix server" -l
- zbxtool -s 【URL】 -u 【USERNAME】 -p 【PASSWORD】 hosttpl --hosts "Zabbix server" -a [TEMPLATE_NAME]
- zbxtool -s 【URL】 -u 【USERNAME】 -p 【PASSWORD】 hosttpl --hosts "Zabbix server" -c [TEMPLATE_NAME]
- zbxtool -s 【URL】 -u 【USERNAME】 -p 【PASSWORD】 hosttpl --hosts "Zabbix server" -u [TEMPLATE_NAME]
- zbxtool -s 【URL】 -u 【USERNAME】 -p 【PASSWORD】 hosttpl --hosts "Zabbix server" -r [TEMPLATE_NAME] -t [TEMPLATE_NAME]
- zbxtool -s 【URL】 -u 【USERNAME】 -p 【PASSWORD】 hosttpl -g "Zabbix servers" -l
- zbxtool -s 【URL】 -u 【USERNAME】 -p 【PASSWORD】 hosttpl -g "Zabbix servers" -a [TEMPLATE_NAME]
- zbxtool -s 【URL】 -u 【USERNAME】 -p 【PASSWORD】 hosttpl -g "Zabbix servers" -c [TEMPLATE_NAME]
- zbxtool -s 【URL】 -u 【USERNAME】 -p 【PASSWORD】 hosttpl -g "Zabbix servers" -u [TEMPLATE_NAME]
- zbxtool -s 【URL】 -u 【USERNAME】 -p 【PASSWORD】 hosttpl -g "Zabbix servers" -r [TEMPLATE_NAME] -t [TEMPLATE_NAME]
- zbxtool -s 【URL】 -u 【USERNAME】 -p 【PASSWORD】 inventory_supplementary
- zbxtool -s 【URL】 -u 【USERNAME】 -p 【PASSWORD】 ldap_usergrp --create-zbx-usrgrp
- zbxtool -s 【URL】 -u 【USERNAME】 -p 【PASSWORD】 ldap_usergrp --create-ldap-group -s 10.189.67.14 -u "cn=Manager,dc=shchinafortune,dc=local" -p [LDAP_PASSWORD]
- zbxtool -s 【URL】 -u 【USERNAME】 -p 【PASSWORD】 ldap_usergrp --create-zbx-usrgrp --create-ldap-group -s 10.189.67.14 -u "cn=Manager,dc=shchinafortune,dc=local" -p [LDAP_PASSWORD]
- zbxtool -s 【URL】 -u 【USERNAME】 -p 【PASSWORD】 multi_interfaces -f ip_range.json --check_agent
- zbxtool -s 【URL】 -u 【USERNAME】 -p 【PASSWORD】 multi_interfaces -f ip_range.json --check_agent --dump excel
- zbxtool -s 【URL】 -u 【USERNAME】 -p 【PASSWORD】 multi_interfaces -f ip_range.json --add_extra
- zbxtool -s 【URL】 -u 【USERNAME】 -p 【PASSWORD】 multi_interfaces -f ip_range.json --delete_invaild
- zbxtool -s 【URL】 -u 【USERNAME】 -p 【PASSWORD】 multi_interfaces -f ip_range.json --delete_extra
- zbxtool -s 【URL】 -u 【USERNAME】 -p 【PASSWORD】 oob -t
- zbxtool -s 【URL】 -u 【USERNAME】 -p 【PASSWORD】 oob -ro
- zbxtool -s 【URL】 -u 【USERNAME】 -p 【PASSWORD】 oob -rs
- zbxtool -s 【URL】 -u 【USERNAME】 -p 【PASSWORD】 send_to_all_users -m "Email" -a "test mail 0916"
- zbxtool -s 【URL】 -u 【USERNAME】 -p 【PASSWORD】 service_tree create -n test10 -g "Discovered hosts" -t Application -s "SLA:2"
- zbxtool -s 【URL】 -u 【USERNAME】 -p 【PASSWORD】 service_tree delete -n test
- zbxtool -s 【URL】 -u 【USERNAME】 -p 【PASSWORD】 sync_wework_media -c [CORPID] -s [SECRET] -a [AGENTID] -d "华鑫运管平台-测试" -g "运管平台 admins" --allow-update
- zbxtool -s 【URL】 -u 【USERNAME】 -p 【PASSWORD】 update_hostgrp_poc -c Contacts.json -l 10.189.67.14 -u cn=Manager,dc=shchinafortune,dc=local -p [LDAP PASSWORD]
- zbxtool -s 【URL】 -u 【USERNAME】 -p 【PASSWORD】 update_hostname
- zbxtool -s 【URL】 -u 【USERNAME】 -p 【PASSWORD】 vmware_host_inventory -l 10.189.67.10 -l 10.189.67.201
- zbxtool -s 【URL】 -u 【USERNAME】 -p 【PASSWORD】 delete_user_media -m WeChat wework-sendmsg 
