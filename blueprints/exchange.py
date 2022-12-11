import json
from datetime import datetime
import requests

from config.exts import db
from config.models import CookiesModel
from utils.utils import send_to_wecom


def Reset():
    cookies_list = CookiesModel.query.all()
    for cookies in cookies_list:
        cookies.convertibility = 1
    db.session.commit()


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
                send_to_wecom(cookies.qq + '碎片兑换成功！请及时查收！\n当前时间：' + today)
                cookies_c = CookiesModel.query.filter_by(qq=cookies.qq).first()
                cookies_c.convertibility = 0
                db.session.commit()
            elif '请先登录' in result:
                cookies_p = CookiesModel.query.filter_by(qq=cookies.qq).first()
                cookies_p.past_due = 1
                db.session.commit()
                send_to_wecom(cookies.qq + '的cookies已过期，请及时更新！\n当前时间：' + today)
            elif '体验币不足' in result:
                cookies_p = CookiesModel.query.filter_by(qq=cookies.qq).first()
                cookies_p.convertibility = 0
                db.session.commit()
                print(cookies.qq + '的体验币不足！\n当前时间：' + today)
            else:
                print(cookies.qq + '的cookies正常！\n当前时间：' + today)
