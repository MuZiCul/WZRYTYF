import json
import random
import string

import requests

from config.config import WECOM_SECRET_KEY


def getRandomLD(length):
    strs = ""
    num = string.ascii_letters + string.digits
    for i in range(length):
        strs += random.choice(num)
    return strs


def send_to_wecom(msg):
    url = f"http://101.126.86.100:22818/send?msg={msg}&secret_key={WECOM_SECRET_KEY}&recipient=LiJinQiang"

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
