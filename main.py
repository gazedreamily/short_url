import aiomysql
import tornado.ioloop
import tornado.web
import datetime
import random
import string
import time
import hashlib
import base64
import hmac
from urllib.parse import urlparse, urlunparse
import yaml

with open("config.yaml") as f:
    config = yaml.safe_load(f)
host = config['database']['host']
port = int(config['database']['port'])
user = config['database']['user']
password = config['database']['password']
database = config['database']['database']
secret = config['sign']['secret']
server_port = config['server']['port']
server_url = f"{config['server']['protocol']}://{config['server']['host']}:{server_port}"


class UrlHandler(tornado.web.RequestHandler):
    @staticmethod
    async def get_sources():
        conn = await aiomysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            db=database
        )
        async with conn.cursor() as cursor:
            await cursor.execute('SELECT source FROM urlList')
            ret = await cursor.fetchall()
        conn.close()
        return tuple([i[0] for i in ret])

    @staticmethod
    async def get_redirect_url(code):
        conn = await aiomysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            db=database
        )
        sql = f"SELECT id, source, target, createTime, expireTime From urlList where source = '{code}';"
        async with conn.cursor() as cursor:
            await cursor.execute(sql)
            ret = await cursor.fetchall()
        conn.close()
        if ret == ():
            return {}
        url_info = {
            "id": ret[0][0],
            "source": ret[0][1],
            "target": ret[0][2],
            "createTime": ret[0][3],
            "expireTime": ret[0][4]
        }
        return url_info

    @staticmethod
    async def get_is_expired(url_info):
        if url_info == {}:
            return True
        expire_time = url_info.get("expireTime")
        if expire_time is None or expire_time >= datetime.datetime.now():
            return False
        sql = f"Delete From urlList where id = {url_info.get('id')};"
        conn = await aiomysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            db=database
        )
        async with conn.cursor() as cursor:
            await cursor.execute(sql)
            await conn.commit()
        conn.close()
        return True

    async def insert_url(self, url, sources, expire_time=None):
        sql = f"SELECT id, source, target, createTime, expireTime From urlList where target = '{url}';"
        conn = await aiomysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            db=database
        )
        async with conn.cursor() as cursor:
            await cursor.execute(sql)
            ret = await cursor.fetchall()
        if ret != ():
            url_info = {
                "id": ret[0][0],
                "source": ret[0][1],
                "target": ret[0][2],
                "createTime": ret[0][3],
                "expireTime": ret[0][4]
            }
            if not await self.get_is_expired(url_info) and expire_time is not None\
                    and ret[0][4] == datetime.datetime.fromtimestamp(int(expire_time)):
                return url_info.get("source")
        new_source = ""
        while new_source == "" or new_source in sources:
            new_source = "".join(random.sample(string.ascii_letters, 7))
        if expire_time is None:
            sql = "INSERT INTO urlList (`source`, `target`, `createTime`) VALUES " \
                  f"('{new_source}', '{url}', '{datetime.datetime.now()}');"
            async with conn.cursor() as cursor:
                await cursor.execute(sql)
                await conn.commit()
            conn.close()
            return new_source
        expire = datetime.datetime.fromtimestamp(int(expire_time))
        if ret != () and expire == ret[0][4]:
            return ret[0][1]
        sql = "INSERT INTO urlList (`source`, `target`, `createTime`, `expireTime`) VALUES " \
              f"('{new_source}', '{url}', '{datetime.datetime.now()}', '{expire}');"
        async with conn.cursor() as cursor:
            await cursor.execute(sql)
            await conn.commit()
        conn.close()
        return new_source

    @staticmethod
    async def gen_sign(timestamp):
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(hmac_code).decode('utf-8')
        return sign

    async def get(self):
        source = self.request.path[1:]
        url_info = await self.get_redirect_url(source)
        if not await self.get_is_expired(url_info):
            self.redirect(url_info["target"])
            return
        self.set_status(404)
        self.write("")

    async def post(self):
        timestamp = self.get_argument("ts", None)
        if abs(int(timestamp) - round(time.time())) > 600:
            self.set_status(404)
            self.write("")
        sign = self.get_argument("sign", None)
        if sign is None or sign != await self.gen_sign(timestamp):
            self.set_status(403)
            self.write("")
        target = self.get_argument("target", None)
        if target is None:
            self.set_status(404)
            self.write("")
        parsed_url = urlparse(target)
        https = self.get_argument("https", "0")
        proto = "https" if https == "1" else "http"
        if not parsed_url.scheme:
            parsed_url = parsed_url._replace(scheme=proto)
        final_url = urlunparse(parsed_url).replace("///", "//")
        sources = await self.get_sources()
        expire_timestamp = self.get_argument("expire", None)
        url_info = await self.insert_url(final_url, sources, expire_timestamp)
        self.write(host + url_info)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            ("/.*", UrlHandler),
            (server_url + "/.*", UrlHandler)
        ]
        tornado.web.Application.__init__(self, handlers)


if __name__ == '__main__':
    app = Application()
    app.listen(server_port)
    tornado.ioloop.IOLoop.current().start()

