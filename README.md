# short_url
![maven](https://img.shields.io/badge/python-3.8%2B-blue)
![maven](https://img.shields.io/badge/tornado-6.2-green)
![maven](https://img.shields.io/badge/aiomysql-0.1.1-orange)

An asynchronous short link backend written in Python based on Tornado and aiomysql

[简体中文](./README_CN.md) | English

## Run

### Clone code and enter the dir
```shell
git clone https://github.com/gazedreamily/short_url.git
cd short_url
```

### Connect to your mysql database
```shell
mysql -u [your mysql username] -p
```

### Create table
```sql
use [database name]
source [project dir]/surl.sql;
```

### Change configuration file
default content of configuration file
```yaml
database: # configuration of database
  host: # servername of database server
  port: # port of database server
  user: # username of database server
  password: # password of database server
  database: # name of database on database server

sign: # configuration of authentication
  secret: # secret when adding new url

server: # configuration of web server
  host: # servername of web server
  port: # port of web server
  protocol: # protocol of web server（http、https）
  ssl: # https(TODO)
    cert:
    key:
```
fill in the configuration file according to your own situation before running

### Install the operating environment
Linux
```shell
pip3 install -r requirements.txt
```

Windows
```shell
pip install -r requirements.txt
```

### just run it!
Linux
```shell
python3 main.py
```

Windows
```shell
python main.py
```

## Usage
### Visit
Use this server configuration like this
```yaml
server:
  host: a.com
  port: 80
  protocol: http
```
The domain name in the database is recorded as

| id  | source  | target              |  createTime  | expireTime |
|-----|---------|---------------------|--------------| -----------|
| 1   | AbcdEfg | https://google.com/ |              |            |

When accessing `http://a.com/AbcdEfg` , the target will be redirected to `https://google.com/`.

The server will return `404` if there is no source record in the database.

### ExpireTime
When accessing a link, the backend will judge whether the current link has expired. If the link expires, it will delete the link from the database and return `404` 

### Insert a link
You can use `client.py` to do it.

When inserting a link, the post carries target_url, current timestamp, signature based on timestamp and secret key, and expiration time (optional).
