import json
import re
from urllib.parse import unquote

import requests
from flask import Blueprint, render_template, request, jsonify

from config.exts import db
from config.models import CookiesModel

bp = Blueprint('index', __name__, url_prefix='/')


@bp.route('/')
def home():
    return render_template('index.html')


@bp.route('/curl', methods=['GET', 'POST'])
def get_curl():
    if request.method == 'POST':
        curl = request.form.get('curl')
        curl_re_expression = re.compile("curl(.*?)--compressed", re.S) or re.compile("curl(.*?)--insecure", re.S)
        curl_result_list = re.findall(curl_re_expression, curl)
        if curl_result_list:
            return curl2py(curl_result_list)
        else:
            return jsonify({'code': 400, 'msg': 'curl格式有误'})
    else:
        return jsonify({'code': 400, 'msg': '系统错误'})


@bp.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        qq = request.form.get('qq')
        cookies = CookiesModel.query.filter_by(qq=qq).first()
        if cookies is None:
            return jsonify({'code': 302})
        c_state = cookies.convertibility
        p_state = cookies.past_due
        return jsonify({'code': 200, 'c_state': c_state, 'p_state': p_state})
    else:
        return jsonify({'code': 400, 'msg': '系统错误'})


def curl2py(curl_result_list):
    try:
        if curl_result_list:
            curl_result = curl_result_list[0]
            # 解析QQ号
            qq_re_expression = re.compile("ied_qq=(.*?);", re.S)
            qq_result_list = re.findall(qq_re_expression, curl_result)
            qq = qq_result_list[0][1:]
            if qq[0] == '0':
                qq = qq[1:]
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
                    msg = add_cookies(qq, url, headers, data_dict) + '，今日兑换成功！'
                    code = 200
                elif '每天只能兑换一次该奖励' in response_msg:
                    msg = add_cookies(qq, url, headers, data_dict) + '，今日已兑换！'
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


def add_cookies(qq, url, headers, data_dict):
    headers_data = str(headers)
    data_data = str(data_dict)
    cookies = CookiesModel.query.filter_by(qq=qq).first()
    if cookies is None:
        cookies_model = CookiesModel(qq=qq, url=url, headers=headers_data, data=data_data, convertibility=0, past_due=0)
        db.session.add(cookies_model)
        db.session.commit()
        return '已添加'
    else:
        cookies.url = url
        cookies.headers = headers_data
        cookies.data = data_data
        cookies.convertibility = 0
        cookies.past_due = 0
        db.session.commit()
        return '已更新'
