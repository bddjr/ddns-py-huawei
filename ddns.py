if __name__ != "__main__":
    raise TypeError('不支持作为模块导入')

try:
    print(
'''ddns-py-huawei 启动！
一款用于华为云的 DDNS 工具。
版本：1.0.3
作者：bddjr
仓库：https://github.com/bddjr/ddns-py-huawei
=============================================='''
    )

    # 参考 https://console.huaweicloud.com/apiexplorer/#/openapi/DNS/sdk?api=ListPublicZones

    #Py3自带模块
    import json, time, sys, copy, os, re
    from typing import Any
    
    def logger(text):
        if isinstance(text, dict) or isinstance(text, list):
            try:
                text = json.dumps(text, indent=4)
            except: pass
        print("[{}] {}".format(
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            text
        ))

    #Py3可能不自带的模块
    notChecked_pip3 = False
    def pip_install(name: str):
        global notChecked_pip3
        if notChecked_pip3:
            logger(f'检查 pip3 命令')
            cmd = 'pip3 -V'
            print(cmd)
            status = os.system(cmd)
            if status != 0:
                logger(f'请先安装 pip3 。:(')
                exit()
            notChecked_pip3 = False

        logger('尝试使用清华源安装模块 '+name)
        cmd = f'pip3 install {name} -i https://pypi.tuna.tsinghua.edu.cn/simple'
        print(cmd)
        status = os.system(cmd)
        print()
        if status == 0:
            return

        logger('尝试直接安装模块 '+name)
        cmd = f'pip3 install {name}'
        print(cmd)
        status = os.system(cmd)
        print()
        if status == 0:
            return

        logger(f'模块 {name} 安装失败，请检查是否联网。:(')
        exit()

    try: import requests
    except: 
        pip_install('requests')
        import requests

    try: from huaweicloudsdkcore.auth.credentials import BasicCredentials
    except:
        pip_install('huaweicloudsdkcore')
        from huaweicloudsdkcore.auth.credentials import BasicCredentials
    # from huaweicloudsdkcore.exceptions import exceptions

    try: from huaweicloudsdkdns.v2.region.dns_region import DnsRegion
    except:
        pip_install('huaweicloudsdkdns')
        from huaweicloudsdkdns.v2.region.dns_region import DnsRegion
    from huaweicloudsdkdns.v2 import *

    del pip_install

    # 读配置
    dirname = os.path.dirname(__file__)

    config_filepath = 'ddns.py.config.json'
    mode = None

    # 通过命令行参数，自动获得模式编号
    for i in sys.argv:
        s = str.strip(i)
        if s.startswith('configfile='):
            config_filepath = s[len('configfile=') : ]
        elif s.startswith('mode='):
            mode = s[len('mode=') : ]

    logger('读取配置文件 ' + config_filepath)
    config_filepath = os.path.join(dirname, config_filepath)
    if not os.path.exists(config_filepath):
        logger('找不到配置文件')
        if str.lower(str.strip(input('您需要生成配置文件模板吗？(y/n)'))).startswith('y'):
            open(config_filepath, 'x', encoding='utf-8').write(json.dumps({
                "access_key_id": "",
                "secret_access_key": "",
                "type": "A",
                "get_ip_from": "https://4.ipw.cn",
                "name": "example.com",
                "ttl": 10,
                "region": "cn-south-1" #广州
            }, indent=4))
            logger('配置文件模板已生成，请在配置文件里填写 name（域名） api_key（API密钥） zone_id（区域ID）')
        else:
            logger('您已取消')
        exit()

    try:
        f = open(config_filepath, 'r', encoding='utf-8')
    except Exception as e:
        logger(e)
        logger('配置文件读取失败，请检查文件权限。:(')
        exit()
    try:
        config = json.load(f)
    except:
        logger('配置文件读取失败，JSON格式错误。:(')
        exit()
    f.close()
    del f
    del config_filepath

    try:
        config = {
            "access_key_id": str.strip(config['access_key_id']),
            "secret_access_key": str.strip(config['secret_access_key']),
            "type": str.upper(str.strip(config['type'])),
            "get_ip_from": str.strip(config['get_ip_from']),
            "name": str.lower(str.strip(config['name'])),
            "ttl": int(config['ttl']),
            "region": str.lower(str.strip(config['region']))
        }
    except Exception as e:
        logger(e)
        logger('配置文件读取失败，请检查是否有缺失的项，或类型是否正确，可尝试将配置文件删除或重命名，然后运行程序重新生成再填写。')
        exit()
    
    if config["access_key_id"]=="" or config["secret_access_key"]=="":
        logger('从 credentials.csv 读取访问密钥')
        credentials_csv_filepath = os.path.join(dirname, 'credentials.csv')
        if not os.path.exists(credentials_csv_filepath):
            logger('找不到文件。:(')
            exit()
        try:
            f = open(credentials_csv_filepath, 'r', encoding='utf-8')
        except Exception as e:
            logger(e)
            logger('读取失败，请检查文件权限。:(')
            exit()
        try:
            if f.readline().strip() != 'User Name,Access Key Id,Secret Access Key':
                raise
            [config["access_key_id"], config["secret_access_key"]] = f.readline().strip().split(',')[-2:]
        except:
            logger('读取失败，格式错误。:(')
            exit()
        

    def pixel_str(instr):
        return instr[0:3] + "*" * (len(instr)-6) + instr[-3:]

    printconfig = copy.deepcopy(config)
    printconfig['access_key_id'] = pixel_str(printconfig['access_key_id'])
    printconfig['secret_access_key'] = pixel_str(printconfig['secret_access_key'])
    logger(printconfig)
    del printconfig

    b = False
    if config['access_key_id'] == '':
        logger('【错误】请在配置文件里填写 access_key_id')
        b = True
    if config['secret_access_key'] == '':
        logger('【错误】请在配置文件里填写 secret_access_key')
        b = True
    if config['name'] in ['','example.com']:
        logger('【错误】请在配置文件里填写 name（域名）')
        b = True
    if config['ttl'] < 1:
        logger('【错误】TTL不得小于1秒！')
        b = True
    if config['region'] == '':
        logger('【错误】请在配置文件里填写region')
        b = True

    if b:
        exit()
    del b

    config_getipform_lower = str.lower(config['get_ip_from'])
    if config['type'] == "A":
        if config_getipform_lower in ["https://6.ipw.cn","http://6.ipw.cn"]:
            logger('【错误】A记录是用于IPv4的，但您错误地将get_ip_from填写为获取IPv6的，请改成 https://4.ipw.cn')
            exit()
        logger('【提醒】请预先确认您的网络支持公网IPv4再使用。')
        ipRegexp = re.compile(r'(\d{1,3}\.){3}\d{1,3}')
    elif config['type'] == "AAAA":
        if config_getipform_lower in ["https://4.ipw.cn","http://4.ipw.cn"]:
            logger('【错误】AAAA记录是用于IPv6的，但您错误地将get_ip_from填写为获取IPv4的，请改成 https://6.ipw.cn')
            exit()
        logger('【提醒】请预先确认您的网络支持公网IPv6再使用。家庭宽带可能需要将光猫、路由器的防火墙关闭（会暴露所有IPv6端口！）')
        ipRegexp = re.compile(r'([0-9a-fA-F]{1,4})?(::?[0-9a-fA-F]{1,4}){1,7}')
    else:
        logger(f'【错误】该程序不支持{config['type']}类型记录！请修改type')
        exit()
    del config_getipform_lower

    print('—————————————————————————')


    modelist = [
        '1 更新记录后退出',
        '2 循环检查IP变化并更新记录',
        '3 删除记录后退出'
    ]

    # 没有符合的命令行参数，询问
    if mode == None:
        mode = input(
f'''选择操作模式
{'\n'.join(modelist)}
请输入编号：'''
        )
    
    try:
        mode = int(mode)
        print('\n模式：' + modelist[mode-1])
    except:
        print('\n找不到模式，请检查输入是否有误。:(')
        exit()

    del modelist
    print('—————————————————————————')


    credentials = BasicCredentials(config['access_key_id'], config['secret_access_key']) \

    client = DnsClient.new_builder() \
        .with_credentials(credentials) \
        .with_region(DnsRegion.value_of(config['region'])) \
        .build()

    ip = None
    def get_ip():
        logger('获取 IP')
        global ip
        ip = None
        try:
            resp = requests.get(config['get_ip_from'])
        except Exception as e:
            logger(e)
            return
        if resp.status_code > 299:
            logger(f"获取IP失败！HTTP状态码 {resp.status_code}")
            return
        ipMatched = ipRegexp.search(resp.text)
        if ipMatched:
            ip = ipMatched.group(0)
            logger('IP: ' + ip)
        else:
            logger(f"获取IP失败！正则表达式找不到IP")

    def get_zone():
        logger('获取zone')
        try:
            req = ListPublicZonesRequest()
            # 简单筛选根域名，例如 ddns.example.com => example.com
            reqName = re.search(r'[^\.]+\.[^\.]+$', config['name'])
            if reqName:
                req.name = reqName.group()
            resp: ListPublicZonesResponse = client.list_public_zones(req) # type: ignore
            if not resp.status_code or resp.status_code > 299:
                logger(f'获取失败，状态码 {resp.status_code}')
                return False
            zones: list[dict[str,Any]] = resp.to_dict()['zones']
            name: str = config['name']+'.'
            j = None
            for i in zones:
                if name == i['name']:
                    # 一模一样，直接返回
                    return i
                if name.endswith('.'+i['name']):
                    # 目标域名以 i的name 结尾
                    if j == None or len(i['name']) > len(j['name']):
                        # j是空，或 i的name 比 j的name 长
                        j = i
            if j:
                # 返回长度最接近目标域名的zone
                return j
            logger('找不到与name匹配的zone，请检查账号里有没有根域名的DNS。:(')
        except Exception as e:
            logger(e)
            logger('获取zone失败，请检查是否断网。:(')
        return False

    def get_record(zone: dict[str, Any]):
        if not zone:
            return False
        logger('获取解析')
        try:
            req = ListRecordSetsByZoneRequest(
                zone_id = zone['id'],
                search_mode = "equal", # 精确搜索
                type = config['type'],
                name = config['name']
            )
            resp: ListRecordSetsByZoneResponse = client.list_record_sets_by_zone(req) # type: ignore
            if not resp.status_code or resp.status_code > 299:
                logger(f'获取失败，状态码 {resp.status_code}')
                return False
            recordsets: list[dict[str,Any]] = resp.to_dict()['recordsets']
            if len(recordsets) > 0:
                logger('指定类型的指定域名 有 记录')
                if len(recordsets) > 1:
                    logger('【警告】该域名有多条解析，请手动移除多余的解析，否则可能导致DNS服务不能正常工作！')
                return recordsets[0]
            logger('指定类型的指定域名 无 记录')
        except Exception as e:
            logger(e)
            logger('获取解析失败，请检查是否断网。:(')
        return False

    def set_record():
        if ip == None:
            return False
        zone = get_zone()
        if not zone:
            return False
        recordSet = get_record(zone)
        try:
            if recordSet:
                records: list[str] = recordSet['records']
                if len(records) == 1 and records[0] == ip:
                    logger('解析对比IP无变化。')
                    return True
                logger('正在更新解析')
                req = UpdateRecordSetRequest(
                    zone_id = zone['id'],
                    recordset_id = recordSet['id'],
                    body = UpdateRecordSetReq(
                        name = config['name'],
                        type = config['type'],
                        ttl = config['ttl'],
                        records = [ip],
                    )
                )
                resp: UpdateRecordSetResponse = client.update_record_set(req) # type: ignore
            else:
                logger('正在创建解析')
                req = CreateRecordSetRequest(
                    zone_id = zone['id'],
                    body = CreateRecordSetRequestBody(
                        name = config['name'],
                        type = config['type'],
                        ttl = config['ttl'],
                        records = [ip],
                    )
                )
                resp: CreateRecordSetResponse = client.create_record_set(req) # type: ignore
            if not resp.status_code or resp.status_code > 299:
                logger(f'失败，状态码 {resp.status_code}')
                return False
            logger('成功！:D')
            return True
        except Exception as e:
            logger(e)
            logger('解析设置失败，请检查是否断网。:(')
            return False

    if mode == 1:
        get_ip()
        set_record()
    elif mode == 2:
        get_ip()
        update_dns_success = set_record()
        old_ip = ip

        while True:
            if update_dns_success:
                sleep_time = max(config['ttl'], 60)
                logger(f'{sleep_time}秒后检测IP是否变化\n')
            else:
                sleep_time = 30
                logger(f'似乎发生了错误，{sleep_time}秒后重试\n')

            time.sleep(sleep_time)

            get_ip()
            if old_ip == ip and update_dns_success:
                logger('本地对比IP无变化。')
            else:
                update_dns_success = set_record()
                old_ip = ip
    elif mode == 3:
        zone = get_zone()
        if not zone:
            exit()
        recordSet = get_record(zone)
        if not recordSet:
            exit()

        logger('删除解析记录')
        try:
            req = DeleteRecordSetRequest(
                zone_id = zone['id'],
                recordset_id = recordSet['id'],
            )
            resp: DeleteRecordSetResponse = client.delete_record_set(req) # type: ignore
            if not resp.status_code or resp.status_code > 299:
                logger(f'删除失败，状态码 {resp.status_code}')
                exit()
            logger('删除成功！:D')
        except Exception as e:
            logger(e)
            logger('解析删除失败，请检查是否断网。:(')
            exit()


except KeyboardInterrupt:
    print('\nCtrl+C')
