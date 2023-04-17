# short_url
![maven](https://img.shields.io/badge/python-3.8%2B-blue)
![maven](https://img.shields.io/badge/tornado-6.2-green)
![maven](https://img.shields.io/badge/aiomysql-0.1.1-orange)

基于Tornado与aiomysql使用Python语言编写的异步短链接后端

简体中文 | [English](./README.md)

## 运行

### 拉取代码进入目录
```shell
git clone https://github.com/gazedreamily/short_url.git
cd short_url
```

### 连入数据库
```shell
mysql -u 你的mysql用户 -p
```

### 创建数据表
```sql
use 数据库名
source 项目路径/surl.sql;
```

### 更改配置文件
默认配置文件内容
```yaml
database: # 此部分为数据库相关配置
  host: # 数据库主机名（域名）
  port: # 数据库端口号
  user: # 数据库用户名
  password: # 数据库密码
  database: # 数据库名

sign: # 验证相关
  secret: # 新增短链接时的验证秘钥

server: # 服务器相关
  host: # 服务器主机名（域名）
  port: # 服务端口号
  protocol: # 服务器链接协议（http、https）
  ssl: # https证书相关（TODO）
    cert:
    key:
```
运行前请将以上信息根据个人情况填写

### 安装相关库
Linux
```shell
pip3 install -r requirements.txt
```

Windows
```shell
pip install -r requirements.txt
```

### 运行项目
Linux
```shell
python3 main.py
```

Windows
```shell
python main.py
```

## 使用
### 访问
以此server配置为模板
```yaml
server:
  host: a.com
  port: 80
  protocol: http
```
数据库中域名记录为

| id  | source  | target              |  createTime  | expireTime |
|-----|---------|---------------------|--------------| -----------|
| 1   | AbcdEfg | https://google.com/ |              |            |

访问 `http://a.com/AbcdEfg` 时，浏览器会被重定向到 `https://google.com/`

若访问的路径没有对应的目标网址，则会返回404

### 有效时间
当访问链接时，后端会判断当前链接是否过期，若链接过期，则会从数据库中删除该链接，并返回404

### 插入链接
可以使用 `client.py` 插入链接
在插入链接时，post中携带target_url，当前时间戳，基于时间戳和秘钥的签名以及过期时间（可选）
