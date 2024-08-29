import json
from datetime import datetime
import requests

from blueprints.index import updateCookiesLog, updateCookiesStates
from config.config import COOKIES_STATE_SUCCESS, COOKIES_STATE_OVERDUE, COOKIES_STATE_DEFICIT, COOKIES_STATE_PAUSE, COOKIES_STATE_START, COOKIES_STATE_ENDED
from config.exts import db
from config.models import CookiesModel, UpdateLogModel, ArgumentsModel
from utils.serverchan import sc_send
from utils.utils import send_to_wecom
import re


def request_(account, url, headers, data):
    try:
        exp, expscore = get_exp(account)
        response = requests.post(url=url, headers=eval(headers), data=eval(data))
        json_data = json.loads(response.text)
        result = json.loads(response.text).get('ret')
        return int(result), json_data, exp
    except Exception as e:
        send_to_wecom('体验服服务器异常，请检查！\n当前时间：' + str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + '\n错误详情：' + str(e))
        return 404, None, None


def SkinDebris():
    cookies_list = CookiesModel.query.all()
    today = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    wecom_list = []
    for cookies in cookies_list:
        if cookies.states not in [COOKIES_STATE_PAUSE]:
            exchange_task(cookies, wecom_list)
    wecom_msg = ''
    if len(wecom_list) > 0:
        for index, wecom in enumerate(wecom_list):
            wecom_msg += f'A{index}：{wecom}\n'
        send_to_wecom('Time：'+today+'\n'+wecom_msg)


def exchange_task(cookies, wecom_list):
    result, json_data, exp = request_(cookies.account, cookies.url, cookies.headers, cookies.data)
    # result == 900为礼品已发放完
    if result != 404:
        if 0 == result:
            state = COOKIES_STATE_SUCCESS
            updateCookiesLog(cookies.account, cookies.type, cookies.remarks, state, exp)
            updateCookiesStates(cookies.account, state, warn=0)
            cookies.warn = state
            db.session.commit()
            wecom_list.append(cookies.account + '，Success！Exp：'+exp)
        elif 101 == result:
            state = COOKIES_STATE_OVERDUE
            if cookies.warn < 3:
                updateCookiesLog(cookies.account, cookies.type, cookies.remarks, state, exp)
                updateCookiesStates(cookies.account, state, warn=cookies.warn+1)
                cookies.warn = state
                db.session.commit()
                wecom_list.append(cookies.account + '，cookies过期！')
        elif 900 == result:
            state = COOKIES_STATE_ENDED
            if cookies.states != state:
                updateCookiesLog(cookies.account, cookies.type, cookies.remarks, state, exp)
                updateCookiesStates(cookies.account, state, warn=0)
                wecom_list.append(cookies.account + '，礼物兑完！Exp：'+exp)
                cookies.warn = state
                db.session.commit()
        elif '体验币不足' in str(json_data):
            state = COOKIES_STATE_DEFICIT
            if cookies.warn < 3:
                updateCookiesLog(cookies.account, cookies.type, cookies.remarks, state, exp)
                updateCookiesStates(cookies.account, state, warn=cookies.warn+1)
                wecom_list.append(cookies.account + '，体验币不足！Exp：'+exp)
                cookies.warn = state
                db.session.commit()
        elif 600 == result:
            cookies.warn = COOKIES_STATE_SUCCESS
            db.session.commit()
            pass


def CheckWZRY():
    from lxml import etree
    headers_User_Agent = ArgumentsModel.query.filter_by(name='check_header').first().value
    URL = ArgumentsModel.query.filter_by(name='check_url').first().value
    try:
        response = requests.get(url=URL, headers=headers_User_Agent)
        if response.status_code == 200:
            json_data = json.loads(response.text)
            data = json_data['data']['items'][0]
            sTargetTitle = data['sTargetTitle']
            if '体验服' in sTargetTitle:
                tid = data['iId']
                sCreated = data['sTargetIdxTime']
                tUrl = 'https://pvp.qq.com/cp/a20161115tyf/detail.shtml?tid=' + str(tid)
                update_list = UpdateLogModel.query.filter_by(update_id=tid).all()
                if len(update_list) < 1:
                    update_log_model = UpdateLogModel(update_date=sCreated, update_id=tid, url=tUrl)
                    db.session.add(update_log_model)
                    db.session.commit()
                    URL = 'https://apps.game.qq.com/wmp/v3.1/public/searchNews.php?p0=18&source=web_pc&id=' + str(tid)
                    response = requests.get(url=URL, headers=headers_User_Agent)
                    data1 = json.loads(response.text[14:-1])['msg']['sContent']
                    data = etree.HTML(text=data1)
                    result = data.xpath('string(.)')
                    sc_send('体验服又更新啦！', result)
                    msgList = []
                    if '更新时间' not in result:
                        msgList = reMsg(result, msgList)
                    else:
                        msgList = get_send_msg(result, tUrl, msgList)
                    for i in msgList:
                        send_to_wecom(i)
        else:
            send_to_wecom('王者体验服监听服务异常！response.status_code != 200')
            sc_send('体验服监听服务异常！', '王者体验服监听服务异常！response.status_code != 200')
    except Exception as e:
        send_to_wecom('王者体验服监听服务异常！\n错误详情：\n' + str(e))
        sc_send('体验服监听服务异常！', '错误详情：\n' + str(e))


def extract_between_chars(s, start, end):
    idx1 = s.index(start)
    idx2 = s.index(end)

    output = s[idx1 + len(start): idx2]
    if output:
        return output
    else:
        return ''


def get_send_msg(result, tUrl, msgList):
    time = extract_between_chars(result, '【更新时间】', '【更新方式】')
    type = extract_between_chars(result, '【更新方式】', '【更新范围】')
    range = extract_between_chars(result, '【更新范围】', '【下载地址】')
    content = result.split('【更新内容】')[1]
    msgList.append(
        '体验服又更新啦，请及时查看并更新！<a href=\"' + tUrl + '\">点击查看更新内容</a>\n更新时间：' + time + '更新方式：' + type + '更新范围：' + range)
    msgList = reMsg(content, msgList)
    return msgList


def reMsg(msg, msgList):
    if len(msg) > 800:
        s = msg[:800]
        result_index = find_last_keyword_position(s)
        if result_index == 0 or result_index is None:
            return msgList
        msgList.append(msg[:result_index])
        return reMsg(msg[result_index:], msgList)
    else:
        msgList.append(msg)
        return msgList


def find_last_keyword_position(s):
    matches = list(re.finditer(r'\n\d', s))
    if matches:
        return matches[-1].start()
    else:
        matches1 = list(re.finditer(r'\n\d', s))
        if not matches and matches1:
            return matches1[-1].start()
        return None


def get_exp(account):
    cookies = CookiesModel.query.filter_by(account=account).first()
    headers = cookies.headers
    url = ArgumentsModel.query.filter_by(name='exp_url').first().value
    data = ArgumentsModel.query.filter_by(name='exp_data').first().value
    try:
        response = requests.post(url=url, headers=eval(headers), data=eval(data))
        json_data = json.loads(response.text)
        exp_voucher = json_data.get('modRet').get('jData').get('exp_voucher')
        expscore = json_data.get('modRet').get('jData').get('expscore')
        return exp_voucher, expscore
    except Exception as e:
        return -1, -1
