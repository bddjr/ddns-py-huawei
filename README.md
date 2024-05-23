# ddns-py-huawei
一款用于华为云的 DDNS 工具。  

cloudflare: https://github.com/bddjr/ddns-py  

```
ddns-py-huawei 启动！
一款用于华为云的 DDNS 工具。
版本：1.0.2
作者：bddjr
仓库：https://github.com/bddjr/ddns-py-huawei
==============================================
[2024-05-23 08:55:15] 读取配置文件 ddns.py.config.json
[2024-05-23 08:55:15] 从 credentials.csv 读取访问密钥
[2024-05-23 08:55:15] {
    "access_key_id": "AIF**************IOF",
    "secret_access_key": "QTx**********************************nzc",        
    "type": "A",
    "get_ip_from": "https://4.ipw.cn",
    "name": "🔣🔣🔣🔣",
    "ttl": 10,
    "region": "cn-south-1"
}
[2024-05-23 08:55:15] 【提醒】请预先确认您的网络支持公网IPv4再使用。        
—————————————————————————
选择操作模式
1 更新记录后退出
2 循环检查IP变化并更新记录
3 删除记录后退出
请输入编号：1

模式：1 更新记录后退出
—————————————————————————
[2024-05-23 08:55:18] 获取 IP
[2024-05-23 08:55:19] IP: 🔣🔣🔣🔣
[2024-05-23 08:55:19] 获取zone
[2024-05-23 08:55:19] 获取解析
[2024-05-23 08:55:19] 指定类型的指定域名 无 记录
[2024-05-23 08:55:19] 正在创建解析
[2024-05-23 08:55:20] 成功！:D
```

***
## 配置

### ip
如果使用IPv4（A），请确认您的网络支持公网IPv4。
```
    "type": "A",
    "get_ip_from": "https://4.ipw.cn",
```

如果使用IPv6（AAAA），请确认您的网络支持公网IPv6。家庭宽带可能需要将光猫、路由器的防火墙关闭（会暴露所有IPv6端口！）
```
    "type": "AAAA",
    "get_ip_from": "https://6.ipw.cn",
```

### access_key_id 与 secret_access_key
请在 https://console.huaweicloud.com/iam/#/mine/accessKey 创建访问密钥，  
然后将下载的 `credentials.csv` 放在与 `ddns.py` 相同的目录即可。  

`ddns.py.config.json` 内留空的这两个配置会自动从 `credentials.csv` 读取。  

### name
填写您想要DDNS的域名。

### ttl
填写DNS缓存时间（单位：秒）。

### region
华为云API服务器所在区域，参考 https://developer.huaweicloud.com/endpoint?DNS

***
## 启动
### Windows
预先安装python3  
然后双击 `ddns.py.bat` 启动，或者在命令行输入 `py ddns.py`  

### Ubuntu
```
apt install python3 python3-pip
python3 ddns.py
```

***
## 命令行参数
### 使用命令行参数跳过询问模式
在命令后面按照如下格式加上参数  
```
mode=2
```
其中 `=` 后面是模式编号，请参照下方列出的编号进行修改，不得在等号两侧添加空格。  
```
1 更新记录后退出
2 循环检查IP变化并更新记录
3 删除记录后退出
```

### 使用命令行参数指定配置文件读取路径
在命令后面按照如下格式加上参数  
```
configfile=ddns.py.config.json
```
其中 `=` 后面是配置文件所在的相对路径或绝对路径，相对路径参照`ddns.py`所在文件夹，而非命令行所在文件夹。  
不得在等号两侧添加空格。  
