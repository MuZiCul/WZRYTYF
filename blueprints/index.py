import json
import re
from datetime import datetime
from urllib.parse import unquote

import requests
from flask import Blueprint, render_template, request, jsonify, flash
from sqlalchemy import and_

from config.config import COOKIES_STATE_ADD, COOKIES_STATE_UPDATE, COOKIES_STATE_SUCCESS, COOKIES_STATE_DEFICIT, \
    COOKIES_STATE_OVERDUE, TYPE_WX, TYPE_QQ
from config.exts import db
from config.models import CookiesModel, CookiesLogModel
from utils.utils import IsNull, IsNotNull

bp = Blueprint('index', __name__, url_prefix='/')


@bp.route('/')
def home():
    return render_template('index.html')


@bp.route('/curl', methods=['GET', 'POST'])
def get_curl():
    if request.method == 'POST':
        curl = request.form.get('curl')
        if IsNull(curl):
            return jsonify({'code': 400, 'msg': 'curl格式有误'})
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
                    return jsonify({'code': 400, 'msg': '当前为微信Curl，请输入微信号！'})
                else:
                    openid_re_expression = re.compile("; openid=(.*?);", re.S)
                    openid_result_list = re.findall(openid_re_expression, curl_result)
                    qq = openid_result_list[0]
            else:
                wx = qq
            if IsNotNull(remarks):
                cookies_remarks = CookiesModel.query.filter_by(remarks=remarks).first()
                if cookies_remarks and cookies_remarks.qq != qq:
                    return jsonify({'code': 400, 'msg': '备注被占用，请检查或更换！'})
            if IsNotNull(wx):
                cookies_remarks = CookiesModel.query.filter_by(wx=wx).first()
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
            response = requests.post(url, headers=headers, data=data_dict)
            response_msg = str(json.loads(response.text))
            if '请先登录' in response_msg:
                msg = 'Cookies已过期，请重新登陆后获取curl'
                code = 400
            else:
                if '恭喜您获得了礼包' in response_msg:
                    msg = add_cookies(qq, wx, type_, url, headers, data_dict, remarks) + '，今日兑换成功！'
                    updateCookiesStates(qq, COOKIES_STATE_SUCCESS)
                    updateCookiesLog(wx, type_, remarks, COOKIES_STATE_SUCCESS)
                    code = 200
                elif '只能兑换一次该奖励' in response_msg:
                    msg = add_cookies(qq, wx, type_, url, headers, data_dict, remarks) + '，今日已兑换！'
                    code = 200
                elif '体验币不足' in response_msg:
                    msg = add_cookies(qq, wx, type_, url, headers, data_dict, remarks) + '，体验币不足！！'
                    updateCookiesStates(qq, COOKIES_STATE_DEFICIT)
                    updateCookiesLog(wx, type_, remarks, COOKIES_STATE_DEFICIT)
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


def add_cookies(qq, wx, type_, url, headers, data_dict, remarks):
    headers_data = str(headers)
    data_data = str(data_dict)
    cookies = CookiesModel.query.filter_by(qq=qq).first()
    if not cookies:
        cookies_model = CookiesModel(qq=qq, wx=wx, url=url, headers=headers_data, data=data_data, type=type_, remarks=remarks, states=COOKIES_STATE_ADD)
        db.session.add(cookies_model)
        db.session.commit()
        updateCookiesLog(wx, type_, remarks, COOKIES_STATE_ADD)
        return '已添加'
    else:
        cookies.url = url
        cookies.headers = headers_data
        cookies.data = data_data
        cookies.wx = wx
        cookies.remarks = remarks
        cookies.type = type_
        cookies.states = COOKIES_STATE_UPDATE
        db.session.commit()
        updateCookiesLog(wx, type_, remarks, COOKIES_STATE_UPDATE)
        return '已更新'


def updateCookiesLog(qq, type_, remarks, states):
    if states == COOKIES_STATE_OVERDUE:
        cookies_OVERDUE = CookiesLogModel.query.filter(
            and_(CookiesLogModel.qq == qq, CookiesLogModel.states == COOKIES_STATE_OVERDUE,
                 db.cast(CookiesLogModel.create_date, db.DATE) == db.cast(datetime.now(), db.DATE))).all()
        if not cookies_OVERDUE:
            updateCookiesLog_(qq, type_, remarks, states)
    elif states == COOKIES_STATE_DEFICIT:
        cookies_DEFICIT = CookiesLogModel.query.filter(
            and_(CookiesLogModel.qq == qq, CookiesLogModel.states == COOKIES_STATE_DEFICIT,
                 db.cast(CookiesLogModel.create_date, db.DATE) == db.cast(datetime.now(), db.DATE))).all()
        if not cookies_DEFICIT:
            updateCookiesLog_(qq, type_, remarks, states)
    else:
        updateCookiesLog_(qq, type_, remarks, states)


def updateCookiesLog_(qq, type_, remarks, states):
    cookies_log_model = CookiesLogModel(qq=qq, type=type_, remarks=remarks, states=states)
    db.session.add(cookies_log_model)
    db.session.commit()


def updateCookiesStates(qq, states_):
    cookies = CookiesModel.query.filter_by(qq=qq).first()
    cookies.states = states_
    db.session.commit()


@bp.route('/test', methods=['GET', 'POST'])
def test():
    return render_template('search.html', qq='898621235')

