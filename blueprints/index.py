import json
import re
from datetime import datetime
from urllib.parse import unquote

import requests
from flask import Blueprint, render_template, request, jsonify, flash
from sqlalchemy import and_

from config.config import COOKIES_STATE_ADD, COOKIES_STATE_UPDATE, COOKIES_STATE_SUCCESS, COOKIES_STATE_DEFICIT, \
    COOKIES_STATE_OVERDUE
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
        curl_re_expression = re.compile("curl(.*?)--compressed", re.S) or re.compile("curl(.*?)--insecure", re.S)
        curl_result_list = re.findall(curl_re_expression, curl)
        if curl_result_list:
            return curl2py(curl_result_list, wx, remarks)
        else:
            return jsonify({'code': 400, 'msg': 'curl格式有误'})
    else:
        return jsonify({'code': 400, 'msg': '系统错误'})


@bp.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        keyword = request.args.get('keyword')
        return render_template('search.html', keyword=keyword)
    else:
        return render_template('index.html')


@bp.route('/search_key', methods=['GET', 'POST'])
def search_key():
    if request.method == 'POST':
        keyword = request.form.get('keyword')
        if IsNull(keyword):
            return jsonify({'code': 400, 'msg': '前先填写关键字再查询！'})
        cookies = CookiesModel.query.filter_by(qq=keyword).first()
        cookies = cookies if cookies else CookiesModel.query.filter_by(remarks=keyword).first()
        if not cookies:
            return jsonify({'code': 302})
        return jsonify({'code': 200})
    else:
        return jsonify({'code': 400, 'msg': '系统错误'})


def curl2py(curl_result_list, wx, remarks):
    try:
        if curl_result_list:
            curl_result = curl_result_list[0]
            # 解析QQ号
            qq_re_expression = re.compile("ied_qq=(.*?);", re.S)
            qq_result_list = re.findall(qq_re_expression, curl_result)
            qq = qq_result_list[0][1:]
            if IsNotNull(qq) and qq[0] == '0':
                qq = qq[1:]
            # 如果是wx登录，解析wx
            wx_re_expression = re.compile("wxcode=(.*?);", re.S)
            wx_result_list = re.findall(wx_re_expression, curl_result)
            if IsNotNull(wx_result_list):
                if IsNull(wx):
                    return jsonify({'code': 400, 'msg': '当前为微信Curl，请输入微信号！'})
                else:
                    qq = wx
            if IsNotNull(remarks):
                cookies_remarks = CookiesModel.query.filter_by(remarks=remarks).first()
                if IsNotNull(cookies_remarks) and cookies_remarks.qq != qq:
                    return jsonify({'code': 400, 'msg': '当前备注已被占用！'})
            # 解析出请求Url
            url_re_expression = re.compile("(http.*?)'", re.S)
            url_result_list = re.findall(url_re_expression, curl_result)
            url = url_result_list[0]
            # 解析头文件
            headers_re_expression = re.compile("-H '(.*?)'", re.S)
            headers_result_list = re.findall(headers_re_expression, curl_result)
            headers = {}
            for header_str in headers_result_list:  # 拼接头文件列表为字典类型
                if ":" in header_str:
                    key = header_str.replace(" ", "").split(":", 1)[0]
                    value = header_str.replace(" ", "").split(":", 1)[1]
                    headers[key] = value
            # 解析data：
            data_re_expression = re.compile("--data-raw '(.*?)'", re.S)
            data_result_list = re.findall(data_re_expression, curl_result)
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
                    msg = add_cookies(qq, url, headers, data_dict, remarks) + '，今日兑换成功！'
                    updateCookiesLog(qq, remarks, COOKIES_STATE_SUCCESS)
                    code = 200
                elif '每天只能兑换一次该奖励' in response_msg:
                    msg = add_cookies(qq, url, headers, data_dict, remarks) + '，今日已兑换！'
                    code = 200
                elif '体验币不足' in response_msg:
                    msg = add_cookies(qq, url, headers, data_dict, remarks) + '，体验币不足！！'
                    updateCookiesLog(qq, remarks, COOKIES_STATE_DEFICIT)
                    code = 200
                else:
                    msg = 'Cookies有误，请重新登陆后获取curl！'
                    code = 400
        else:
            msg = 'curl有误！'
            code = 400
        return jsonify({'code': code, 'msg': msg})
    except Exception as e:
        return jsonify({'code': 400, 'msg': '系统错误，错误代码：' + str(e)})


def add_cookies(qq, url, headers, data_dict, remarks):
    headers_data = str(headers)
    data_data = str(data_dict)
    cookies = CookiesModel.query.filter_by(qq=qq).first()
    if IsNull(cookies):
        cookies_model = CookiesModel(qq=qq, url=url, headers=headers_data, data=data_data, remarks=remarks)
        db.session.add(cookies_model)
        db.session.commit()
        updateCookiesLog(qq, remarks, COOKIES_STATE_ADD)
        return '已添加'
    else:
        cookies.url = url
        cookies.headers = headers_data
        cookies.data = data_data
        cookies.remarks = remarks
        db.session.commit()
        updateCookiesLog(qq, remarks, COOKIES_STATE_UPDATE)
        return '已更新'


def updateCookiesLog(qq, remarks, states):
    if states == COOKIES_STATE_OVERDUE:
        cookies_OVERDUE = CookiesLogModel.query.filter(
            and_(CookiesLogModel.qq == qq, CookiesLogModel.states == COOKIES_STATE_OVERDUE,
                 db.cast(CookiesLogModel.create_date, db.DATE) == db.cast(datetime.now(), db.DATE))).all()
        if not cookies_OVERDUE:
            updateCookiesLog_(qq, remarks, states)
    elif states == COOKIES_STATE_DEFICIT:
        cookies_DEFICIT = CookiesLogModel.query.filter(
            and_(CookiesLogModel.qq == qq, CookiesLogModel.states == COOKIES_STATE_DEFICIT,
                 db.cast(CookiesLogModel.create_date, db.DATE) == db.cast(datetime.now(), db.DATE))).all()
        if not cookies_DEFICIT:
            updateCookiesLog_(qq, remarks, states)
    else:
        updateCookiesLog_(qq, remarks, states)


def updateCookiesLog_(qq, remarks, states):
    cookies_log_model = CookiesLogModel(qq=qq, remarks=remarks, states=states)
    db.session.add(cookies_log_model)
    db.session.commit()


@bp.route('/test', methods=['GET', 'POST'])
def test():
    return render_template('search.html', qq='898621235')


@bp.route('/search_data', methods=['GET', 'POST'])
def ssss():
    keyword = request.args.get('keyword')
    result = CookiesLogModel.query.filter_by(qq=keyword).order_by(db.text('-create_date')).all()
    result = result if IsNotNull(result) else CookiesLogModel.query.filter_by(remarks=keyword).order_by(db.text('-create_date')).all()
    data_list = []
    for i in result:
        dit = {'id': i.id, 'qq': i.qq, 'remarks': i.remarks, 'states': i.states,
               'create_date': str(i.create_date) if i.create_date else '暂无信息', }
        data_list.append(dit)
    dic = {'code': 0, 'msg': 'SUCCESS', 'count': len(result), 'data': data_list}
    return json.dumps(dic, ensure_ascii=False)
