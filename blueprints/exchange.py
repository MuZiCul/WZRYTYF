import json
from datetime import datetime
import requests

from blueprints.index import updateCookiesLog
from config.config import COOKIES_STATE_SUCCESS, COOKIES_STATE_OVERDUE, COOKIES_STATE_DEFICIT
from config.exts import db
from config.models import CookiesModel
from utils.utils import send_to_wecom


def request_(url, headers, data):
    today = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    try:
        response = requests.post(url=url, headers=eval(headers), data=eval(data))
        result = str(json.loads(response.text))
        return result, today
    except Exception as e:
        send_to_wecom('体验服服务器异常，请检查！\n当前时间：' + today + '\n错误详情：' + str(e))
        return 0, today


def SkinDebris():
    cookies_list = CookiesModel.query.all()
    for cookies in cookies_list:
        result, today = request_(cookies.url, cookies.headers, cookies.data)
        if result != 0:
            if '恭喜您获得了礼包' in result:
                updateCookiesLog(cookies.qq, cookies.type, cookies.remarks, COOKIES_STATE_SUCCESS)
                send_to_wecom(cookies.qq + '碎片兑换成功！请及时查收！\n当前时间：' + today)
            elif '请先登录' in result:
                updateCookiesLog(cookies.qq, cookies.type, cookies.remarks, COOKIES_STATE_OVERDUE)
                send_to_wecom(cookies.qq + '的cookies已过期，请及时更新！\n当前时间：' + today)
            elif '体验币不足' in result:
                updateCookiesLog(cookies.qq, cookies.type, cookies.remarks, COOKIES_STATE_DEFICIT)
