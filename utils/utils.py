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
    wecom_cid = WECOM_CID
    wecom_aid = WECOM_AID
    wecom_secret = WECOM_SECRET
    wecom_touid = WECOM_TOUID
    get_token_url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={wecom_cid}&corpsecret={wecom_secret}"
    response = requests.get(get_token_url).content
    access_token = json.loads(response).get('access_token')
    if access_token and len(access_token) > 0:
        send_msg_url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}'
        data = {
            "touser": wecom_touid,
            "agentid": wecom_aid,
            "msgtype": "text",
            "text": {
                "content": msg
            },
            "duplicate_check_interval": 600
        }
        response = requests.post(send_msg_url, data=json.dumps(data)).content
        return response
    else:
        return 0


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
