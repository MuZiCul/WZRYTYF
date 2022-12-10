import json
from datetime import datetime
import requests

from config.exts import db
from config.models import CookiesModel
from utils.utils import send_to_wecom

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,en-US;q=0.7,en;q=0.3',
    'Origin': 'https://smoba.ams.game.qq.com',
    'Connection': 'keep-alive',
    'Referer': 'https://smoba.ams.game.qq.com/ams/postMessage_noflash.html',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
}


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
            else:
                send_to_wecom(cookies.qq + '的cookies正常！\n当前时间：' + today)
