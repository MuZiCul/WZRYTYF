import json
from datetime import datetime
import requests

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


def request_(params, cookies, data):
    qq = cookies['ied_qq'][1:]
    today = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    try:
        response = requests.post('https://smoba.ams.game.qq.com/ams/ame/amesvr', params=params, cookies=cookies,
                                 headers=HEADERS, data=data)
        result = str(json.loads(response.text))
        return qq, result, today
    except Exception as e:
        send_to_wecom('体验服服务器异常，请检查！\n当前时间：' + today+ '\n错误详情：'+ str(e))
        return qq, 0, today


def SkinDebris(params, cookies, data):
    qq, result, today = request_(params, cookies, data)
    if result!=0:
        if '恭喜您获得了礼包' in result:
            send_to_wecom(qq + '碎片兑换成功！请及时查收！\n当前时间：' + today)
        else:
            send_to_wecom(qq + '的cookies已过期，请及时更新！\n当前时间：' + today)


def check_cookies(params, cookies, data):
    qq, result, today = request_(params, cookies, data)
    if result != 0:
        if '请先登录' in result:
            send_to_wecom(qq + '的cookies已过期，请及时更新！\n当前时间：' + today)


