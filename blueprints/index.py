import ast
import json
import re
from datetime import datetime
from urllib.parse import unquote

import requests
from flask import Blueprint, render_template, request, jsonify
from sqlalchemy import and_

from blueprints.exchange import CheckWZRY
from config.config import COOKIES_STATE_ADD, COOKIES_STATE_UPDATE, COOKIES_STATE_SUCCESS, COOKIES_STATE_DEFICIT, \
    COOKIES_STATE_OVERDUE, TYPE_WX, TYPE_QQ, COOKIES_STATE_ENDED, COOKIES_STATE_PAUSE
from config.exts import db
from config.models import CookiesModel, CookiesLogModel, ArgumentsModel
from utils.utils import IsNull, IsNotNull, send_to_wecom

bp = Blueprint('index', __name__, url_prefix='/')


@bp.route('/')
def home():
    return render_template('index.html')


@bp.route('/curl', methods=['GET', 'POST'])
def get_curl():
    if request.method == 'POST':
        curl = request.form.get('curl')
        if IsNull(curl):
            return jsonify({'code': 400, 'msg': 'curl为空，请检查！'})
        wx = request.form.get('wx')
        remarks = request.form.get('remarks')
        return curl2py(curl, wx, remarks)
    else:
        return jsonify({'code': 400, 'msg': '系统错误'})


def curl2py(curl, wx, remarks):
    try:
        if curl:
            curl_re_expression = re.compile("curl(.*?)--data-raw", re.S)
            curl_result_list = re.findall(curl_re_expression, curl)
            curl_result = curl_result_list[0]
            # 解析QQ号
            qq_re_expression = re.compile("ams_qqopenid_(.*?);", re.S)
            qq_result = re.findall(qq_re_expression, curl_result)[0]
            qq_re_number = re.compile("%7C(.*?)%7C", re.S)
            qq = re.findall(qq_re_number, qq_result)[0]
            if IsNull(qq):
                return jsonify({'code': 400, 'msg': '未解析到账号，Curl似乎不对哦，请检查！'})
            if IsNotNull(qq) and qq[0] == '0':
                qq = qq[1:]
            type_ = TYPE_QQ
            # 如果是wx登录，解析wx
            wx_re_expression = re.compile("wxcode=(.*?);", re.S)
            wx_result_list = re.findall(wx_re_expression, curl_result)
            if IsNotNull(wx_result_list):
                type_ = TYPE_WX
                if IsNull(wx):
                    return jsonify({'code': 400, 'msg': '判断当前CURL为微信游戏数据，请输入微信号！'})
                else:
                    openid_re_expression = re.compile("; openid=(.*?);", re.S)
                    openid_result_list = re.findall(openid_re_expression, curl_result)
                    qq = openid_result_list[0]
                    account = wx
            else:
                account = qq
            if IsNotNull(remarks):
                cookies_remarks = CookiesModel.query.filter_by(remarks=remarks).first()
                if cookies_remarks and cookies_remarks.qq != qq:
                    return jsonify({'code': 400, 'msg': '备注被占用，请检查或更换！'})
            if IsNotNull(account):
                cookies_remarks = CookiesModel.query.filter_by(account=account).first()
                if cookies_remarks and cookies_remarks.qq != qq:
                    return jsonify({'code': 400, 'msg': '账号被占用，请检查或更换！'})  # 待修改
            # 解析出请求Url
            url_re_expression = re.compile("(http.*?)'", re.S)
            url_result_list = re.findall(url_re_expression, curl_result)
            if IsNull(url_result_list):
                return jsonify({'code': 400, 'msg': 'Curl似乎不对哦，请检查！'})
            url = url_result_list[0]
            # 解析头文件
            headers_re_expression = re.compile("-H '(.*?)'", re.S)
            headers_result_list = re.findall(headers_re_expression, curl_result)
            if IsNull(headers_result_list):
                return jsonify({'code': 400, 'msg': 'Curl似乎不对哦，请检查！'})
            headers = {}
            for header_str in headers_result_list:  # 拼接头文件列表为字典类型
                if ":" in header_str:
                    key = header_str.replace(" ", "").split(":", 1)[0]
                    value = header_str.replace(" ", "").split(":", 1)[1]
                    headers[key] = value
            # 解析data：
            data_re_expression = re.compile("--data-raw '(.*?)'", re.S)
            data_result_list = re.findall(data_re_expression, curl)
            if IsNull(data_result_list):
                return jsonify({'code': 400, 'msg': 'Curl似乎不对哦，请检查！'})
            data = unquote(data_result_list[0])
            data_list = data.split('&')
            data_dict = {}
            for i in data_list:
                i_list = i.split('=', 1)
                data_dict[i_list[0]] = i_list[1]
            data_dict['eas_refer'] = data_dict['eas_refer'] + '&version=' + data_dict['version']
            data_dict.pop('version', '')
            # response = requests.post(url, headers=headers, data=data_dict)
            result, json_data, exp = request_(account, url, headers=headers, data=data_dict)
            # response_msg = str(json.loads(response.text))
            if result == 404:
                msg = 'Cookies已过期，请重新登陆后获取curl！'
                code = 400
            else:
                if '获得了礼包' in str(json_data):
                    state = COOKIES_STATE_SUCCESS
                    msg = add_cookies(qq, account, type_, url, headers, data_dict, remarks, state, exp) + \
                          '，今日兑换成功！'
                    updateCookiesStates(account, state, warn=0)
                    updateCookiesLog(account, type_, remarks, state, exp)
                    code = 200
                elif '兑换一次' in str(json_data):
                    state = COOKIES_STATE_SUCCESS
                    msg = add_cookies(qq, account, type_, url, headers, data_dict, remarks, state, exp) + \
                          '，今日已兑换！'
                    updateCookiesStates(account, state, warn=0)
                    code = 200
                elif '体验币不足' in str(json_data):
                    state = COOKIES_STATE_DEFICIT
                    msg = add_cookies(qq, account, type_, url, headers, data_dict, remarks, state, exp) + \
                          '，账号体验币不足！'
                    updateCookiesStates(account, state, warn=0)
                    updateCookiesLog(account, type_, remarks, state, exp)
                    code = 200
                elif '已发放完' in str(json_data):
                    state = COOKIES_STATE_ENDED
                    msg = add_cookies(qq, account, type_, url, headers, data_dict, remarks, state, exp) + \
                          '，今日皮肤碎片礼品已发放完！'
                    updateCookiesStates(account, state, warn=0)
                    updateCookiesLog(account, type_, remarks, state, exp)
                    code = 200
                else:
                    msg = 'Cookies有误，请重新登陆后获取curl！'
                    code = 400
        else:
            msg = 'curl有误！'
            code = 400
        return jsonify({'code': code, 'msg': msg})
    except Exception as e:
        return jsonify({'code': 400, 'msg': 'Cookies有误，请重新登陆后获取curl，错误代码：' + str(e)})


def add_cookies(qq, account, type_, url, headers, data_dict, remarks, state, exp):
    headers_data = str(headers)
    data_data = str(data_dict)
    cookies = CookiesModel.query.filter_by(account=account).first()
    if not cookies:
        cookies_model = CookiesModel(qq=qq, account=account, url=url, headers=headers_data,
                                     data=data_data, type=type_, remarks=remarks, states=state)
        db.session.add(cookies_model)
        db.session.commit()
        updateCookiesLog(account, type_, remarks, state, exp)
        return '账号添加成功！'
    else:
        cookies.url = url
        cookies.headers = headers_data
        cookies.data = data_data
        cookies.qq = qq
        cookies.remarks = remarks
        cookies.type = type_
        cookies.states = state
        db.session.commit()
        updateCookiesLog(account, type_, remarks, state, exp)
        return '账号更新成功！'


def updateCookiesLog(account, type_, remarks, states, exp):
    if states == COOKIES_STATE_OVERDUE:
        cookies_OVERDUE = CookiesLogModel.query.filter(
            and_(CookiesLogModel.account == account, CookiesLogModel.states == COOKIES_STATE_OVERDUE,
                 db.cast(CookiesLogModel.create_date, db.DATE) == db.cast(datetime.now(), db.DATE))).all()
        if not cookies_OVERDUE:
            updateCookiesLog_(account, type_, remarks, states, exp)
    elif states == COOKIES_STATE_DEFICIT:
        cookies_DEFICIT = CookiesLogModel.query.filter(
            and_(CookiesLogModel.account == account, CookiesLogModel.states == COOKIES_STATE_DEFICIT,
                 db.cast(CookiesLogModel.create_date, db.DATE) == db.cast(datetime.now(), db.DATE))).all()
        if not cookies_DEFICIT:
            updateCookiesLog_(account, type_, remarks, states, exp)
    else:
        updateCookiesLog_(account, type_, remarks, states, exp)


def updateCookiesLog_(account, type_, remarks, states, exp):
    cookies_log_model = CookiesLogModel(account=account, type=type_, remarks=remarks, states=states, exp=exp)
    db.session.add(cookies_log_model)
    db.session.commit()


def updateCookiesStates(account, states_, warn):
    cookies = CookiesModel.query.filter_by(account=account).first()
    cookies.states = states_
    cookies.warn = warn
    db.session.commit()


@bp.route('/test', methods=['GET', 'POST'])
def test():
    CheckWZRY()
    return render_template('search.html', qq='898621235')


def request_(account, url, headers, data):
    try:
        exp, expscore = get_exp(account)
        if isinstance(headers, str):
            headers = ast.literal_eval(headers)
        if isinstance(data, str):
            data = ast.literal_eval(data)
        response = requests.post(url=url, headers=headers, data=data)
        json_data = json.loads(response.text)
        result = json.loads(response.text).get('ret')
        return int(result), json_data, exp
    except Exception as e:
        send_to_wecom('体验服服务器异常，请检查！\n当前时间：' + str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + '\n错误详情：' + str(
            e) + '\n错误位置：request_()')
        return 404, None, None


def get_exp(account):
    cookies = CookiesModel.query.filter_by(account=account).first()
    headers = cookies.headers
    url = ArgumentsModel.query.filter_by(name='exp_url').first().value
    data = ArgumentsModel.query.filter_by(name='exp_data').first().value
    try:
        if isinstance(headers, str):
            headers = ast.literal_eval(headers)
        if isinstance(data, str):
            data = ast.literal_eval(data)
        response = requests.post(url=url, headers=headers, data=data)
        json_data = json.loads(response.text)
        if json_data.get('ret') == '101':
            return -1, -1
        exp_voucher = json_data.get('modRet').get('jData').get('exp_voucher')
        expscore = json_data.get('modRet').get('jData').get('expscore')
        return exp_voucher, expscore
    except Exception as e:
        send_to_wecom('体验服服务器异常，请检查！\n当前时间：' + str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + '\n错误详情：' + str(
            e) + '\n错误位置：get_exp()')
        return -1, -1


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
        send_to_wecom('Time：' + today + '\n' + wecom_msg)


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
            wecom_list.append(cookies.account + '，Success！Exp：' + exp)
        elif 101 == result:
            state = COOKIES_STATE_OVERDUE
            if cookies.warn < 3:
                updateCookiesLog(cookies.account, cookies.type, cookies.remarks, state, exp)
                updateCookiesStates(cookies.account, state, warn=cookies.warn + 1)
                cookies.warn = state
                db.session.commit()
                wecom_list.append(cookies.account + '，cookies过期！')
        elif 900 == result:
            state = COOKIES_STATE_ENDED
            if cookies.states != state:
                updateCookiesLog(cookies.account, cookies.type, cookies.remarks, state, exp)
                updateCookiesStates(cookies.account, state, warn=0)
                wecom_list.append(cookies.account + '，礼物兑完！Exp：' + exp)
                cookies.warn = state
                db.session.commit()
        elif '体验币不足' in str(json_data):
            state = COOKIES_STATE_DEFICIT
            if cookies.warn < 3:
                updateCookiesLog(cookies.account, cookies.type, cookies.remarks, state, exp)
                updateCookiesStates(cookies.account, state, warn=cookies.warn + 1)
                wecom_list.append(cookies.account + '，体验币不足！Exp：' + exp)
                cookies.warn = state
                db.session.commit()
        elif 600 == result:
            cookies.warn = COOKIES_STATE_SUCCESS
            db.session.commit()
            pass
