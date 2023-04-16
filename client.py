import hashlib
import base64
import hmac
import requests
import time


def gen_sign(timestamp, secret):
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
    sign = base64.b64encode(hmac_code).decode('utf-8')
    return sign


if __name__ == '__main__':
    secret = "test"     # the same secret in the config.yaml
    url = "http://localhost:8000/"      # your server address
    ts = round(time.time())
    data = {
        "ts": ts,
        "sign": gen_sign(ts, secret),
        "target": "",
        "https": 1,
        "expire": ""
    }
    r = requests.post(url, data=data)
    print(r.text)

