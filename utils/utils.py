import json
import random
import string

import requests

from config.config import WECOM_CID, WECOM_AID, WECOM_SECRET, WECOM_TOUID


def getRandomLD(length):
    strs = ""
    num = string.ascii_letters + string.digits
    for i in range(length):
        strs += random.choice(num)
    return strs


def send_to_wecom(msg):
    SECRET_KEY = 'j6nD4C-M9KPGFyaT4JrtbezVNZD-tFOLQHpf3Jj1bvO'
    url = f"http://54.251.5.234:22818/message_transfer?msg={msg}&wecom_cid={WECOM_CID}&wecom_aid={WECOM_AID}&wecom_secret={WECOM_SECRET}&wecom_touid={WECOM_TOUID}&secret_key={SECRET_KEY}"

    response = requests.post(url)

    if response.status_code == 200:
        print("请求发送成功！")
        print("响应内容：", response.text)
    else:
        print("请求发送失败！")
        print("错误码：", response.status_code)


def IsNull(obj):
    if obj is None or len(obj)<1 or obj == '' or obj == ' ':
        return True
    else:
        return False


def IsNotNull(obj):
    if obj is None or len(obj)<1 or obj == '' or obj == ' ':
        return False
    else:
        return True
