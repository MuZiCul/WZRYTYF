import json
import re
from datetime import datetime
from urllib.parse import unquote

import requests
from flask import Blueprint, render_template, request, jsonify, flash
from sqlalchemy import and_

from blueprints.exchange import request_
from config.config import COOKIES_STATE_ADD, COOKIES_STATE_UPDATE, COOKIES_STATE_SUCCESS, COOKIES_STATE_DEFICIT, \
    COOKIES_STATE_OVERDUE, TYPE_WX, TYPE_QQ, COOKIES_STATE_PAUSE, COOKIES_STATE_START
from config.exts import db
from config.models import CookiesModel, CookiesLogModel
from utils.utils import IsNull, IsNotNull

bp = Blueprint('search', __name__, url_prefix='/')


@bp.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        keyword = request.args.get('keyword')
        exp_voucher, state, type_ = get_exp_voucher(keyword)
        return render_template('search.html', keyword=keyword, exp_voucher=exp_voucher, state=state, type=type_)
    else:
        return render_template('index.html')


@bp.route('/search_all', methods=['GET', 'POST'])
def search_all():
    if request.method == 'GET':
        keyword = request.args.get('keyword')
        return render_template('search_All.html', keyword=keyword)
    else:
        return render_template('index.html')


@bp.route('/search_key', methods=['GET', 'POST'])
def search_key():
    if request.method == 'POST':
        keyword = request.form.get('keyword')
        if IsNull(keyword):
            return jsonify({'code': 400, 'msg': '请先填写关键字再查询！'})
        cookies = CookiesModel.query.filter_by(qq=keyword).first()
        cookies = cookies if cookies else CookiesModel.query.filter_by(remarks=keyword).first()
        if not cookies:
            return jsonify({'code': 302})
        return jsonify({'code': 200})
    else:
        return jsonify({'code': 400, 'msg': '系统错误'})


@bp.route('/search_data', methods=['GET', 'POST'])
def search_data():
    keyword = request.args.get('keyword')
    result = CookiesLogModel.query.filter_by(qq=keyword).order_by(db.text('-create_date')).all()
    result = result if result else CookiesLogModel.query.filter_by(remarks=keyword).order_by(db.text('-create_date')).all()
    data_list = []
    for i in result:
        dit = {'id': i.id, 'qq': i.qq, 'remarks': i.remarks, 'states': i.states,
               'create_date': str(i.create_date) if i.create_date else '暂无信息', }
        data_list.append(dit)
    dic = {'code': 0, 'msg': 'SUCCESS', 'count': len(result), 'data': data_list}
    return json.dumps(dic, ensure_ascii=False)


@bp.route('/search_all_data', methods=['GET', 'POST'])
def search_all_data():
    keyword = request.args.get('keyword')
    if keyword != 'All':
        dic = {'code': 0, 'msg': 'SUCCESS', 'count': 0, 'data': []}
        return json.dumps(dic, ensure_ascii=False)
    result = CookiesLogModel.query.order_by(db.text('-create_date')).all()
    data_list = []
    for i in result:
        dit = {'id': i.id, 'qq': i.qq, 'remarks': i.remarks, 'states': i.states, 'type': i.type,
               'create_date': str(i.create_date) if i.create_date else '暂无信息', }
        data_list.append(dit)
    dic = {'code': 0, 'msg': 'SUCCESS', 'count': len(result), 'data': data_list}
    return json.dumps(dic, ensure_ascii=False)


def get_exp_voucher(keyword):
    exp_voucher, state, type_ = '未知', '未知', '未知'
    if IsNotNull(keyword):
        cookies = CookiesModel.query.filter_by(qq=keyword).first()
        cookies = cookies if cookies else CookiesModel.query.filter_by(remarks=keyword).first()
        cookies = cookies if cookies else CookiesModel.query.filter_by(wx=keyword).first()
        if cookies:
            result_log = CookiesLogModel.query.filter_by(qq=keyword).order_by(db.text('-create_date')).all()
            result_log = result_log if result_log else CookiesLogModel.query.filter_by(remarks=keyword).order_by(db.text('-create_date')).all()
            result_log = result_log if result_log else CookiesLogModel.query.filter_by(wx=keyword).order_by(
                db.text('-create_date')).all()
            if result_log:
                state = result_log[0].states
                type_ = result_log[0].type
            if state != COOKIES_STATE_OVERDUE:
                result, today = request_(cookies.url, cookies.headers, str(get_exp_voucher_data(eval(cookies.data), type_)))
                try:
                    exp_voucher = eval(result).get('modRet').get('jData').get('exp_voucher')
                except Exception as e:
                    exp_voucher = '未知'
    return exp_voucher, get_cookies_state(state), get_type(type_)


def get_exp_voucher_data(data_, type_):
    new_data = {'sArea': data_['sArea'],
                'appid': '1104791911',
                'iActivityId': data_['iActivityId'],
                'iFlowId': '407548',
                'g_tk': data_['g_tk'],
                'e_code': data_['e_code'],
                'g_code': data_['g_code'],
                'eas_url': data_['eas_url'],
                'eas_refer': data_['eas_refer'],
                'xhr': data_['xhr'],
                'sServiceDepartment': data_['sServiceDepartment'],
                'sServiceType': data_['sServiceType'],
                'xhrPostKey': data_['xhrPostKey']}
    if type_ == TYPE_WX:
        new_data['ams_appname'] = 'YXZJ_TO_TIYAN'
        new_data['ams_targetappid'] = 'wx71a79717188d990b'
    return new_data


def get_type(num):
    if num == TYPE_WX:
        return '微信'
    elif num == TYPE_QQ:
        return 'QQ'
    else:
        return '未知'


def get_cookies_state(num):
    if num == COOKIES_STATE_ADD:
        return '账号新增'
    elif num == COOKIES_STATE_UPDATE:
        return '账号更新'
    elif num == COOKIES_STATE_OVERDUE:
        return 'Curl过期'
    elif num == COOKIES_STATE_SUCCESS:
        return '兑换成功'
    elif num == COOKIES_STATE_DEFICIT:
        return '体验币不足'
    elif num == COOKIES_STATE_PAUSE:
        return '暂停任务'
    elif num == COOKIES_STATE_START:
        return '开始任务'
    else:
        return '未知'
