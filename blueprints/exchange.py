import json
from datetime import datetime
import requests

from blueprints.index import updateCookiesLog, updateCookiesStates
from config.config import COOKIES_STATE_SUCCESS, COOKIES_STATE_OVERDUE, COOKIES_STATE_DEFICIT
from config.exts import db
from config.models import CookiesModel, UpdateLogModel
from utils.utils import send_to_wecom
import re


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
                updateCookiesStates(cookies.qq, COOKIES_STATE_SUCCESS)
                send_to_wecom(cookies.qq + '碎片兑换成功！请及时查收！\n当前时间：' + today)
            elif '请先登录' in result:
                if cookies.states != COOKIES_STATE_OVERDUE:
                    updateCookiesLog(cookies.qq, cookies.type, cookies.remarks, COOKIES_STATE_OVERDUE)
                    updateCookiesStates(cookies.qq, COOKIES_STATE_OVERDUE)
                    send_to_wecom(cookies.qq + '的cookies已过期，请及时更新！\n当前时间：' + today)
            elif '体验币不足' in result:
                if cookies.states != COOKIES_STATE_DEFICIT:
                    updateCookiesLog(cookies.qq, cookies.type, cookies.remarks, COOKIES_STATE_DEFICIT)
                    updateCookiesStates(cookies.qq, COOKIES_STATE_DEFICIT)
                    send_to_wecom(cookies.qq + '的体验币不足！\n当前时间：' + today)
            elif '每天只能兑换一次该奖励' in result:
                pass


def CheckWZRY():
    import datetime
    from lxml import etree
    headers_User_Agent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,en-US;q=0.7,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }
    URL = 'https://apps.game.qq.com/cmc/cross?serviceId=18&filter=channel&sortby=sIdxTime&source=web_pc&limit=6&logic=or&typeids=1&chanid=1766&start=0&exclusiveChannel=4&exclusiveChannelSign=71e03783c3cc69af7bc422532ee43495&time=1670440180'
    try:
        response = requests.get(url=URL, headers=headers_User_Agent)
        if response.status_code == 200:
            json_data = json.loads(response.text)
            data = json_data['data']['items'][0]
            tid = data['iId']
            sCreated = data['sTargetIdxTime']
            dCreated = data['sTargetIdxTime'][:10]
            today = str(datetime.date.today())
            tUrl = 'https://pvp.qq.com/cp/a20161115tyf/detail.shtml?tid=' + str(tid)
            if dCreated == today:
                update_list = UpdateLogModel.query.filter_by(update_date=sCreated).all()
                if len(update_list) < 1:
                    update_list_model = UpdateLogModel(update_date=sCreated, update_url=tUrl)
                    db.session.add(update_list_model)
                    db.session.commit()
                    URL = 'https://apps.game.qq.com/wmp/v3.1/public/searchNews.php?p0=18&source=web_pc&id='+str(tid)
                    response = requests.get(url=URL, headers=headers_User_Agent)
                    data1 = json.loads(response.text[14:-1])['msg']['sContent']
                    data = etree.HTML(text=data1)
                    result = data.xpath('string(.)')
                    msgList = get_send_msg(result,tUrl)
                    for i in msgList:
                        send_to_wecom(i)
        else:
            send_to_wecom('王者体验服监听服务异常！')
    except Exception as e:
        send_to_wecom('王者体验服监听服务异常！\n错误代码：\n'+str(e))


def extract_between_chars(s, start, end):
    idx1 = s.index(start)
    idx2 = s.index(end)

    output = s[idx1 + len(start): idx2]
    if output:
        return output
    else:
        return ''

def get_send_msg(result,tUrl):
    time = extract_between_chars(result,'【更新时间】','【更新方式】')
    type = extract_between_chars(result,'【更新方式】','【更新范围】')
    range = extract_between_chars(result,'【更新范围】','【下载地址】')
    content = result.split('【更新内容】')[1]
    msgList = []
    msgList.append('体验服又更新啦，请及时查看并更新！<a href=\"'+tUrl+'\">点击查看更新内容</a>\n更新时间：'+time+'更新方式：'+type+'更新范围：'+range)
    msgList = reMsg(content, msgList)
    return msgList


def reMsg(msg, msgList):
    if len(msg)>800:
        msgList.append(msg[:800])
        return reMsg(msg[800:], msgList)
    else:
        msgList.append(msg)
        return msgList
