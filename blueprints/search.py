import json
from flask import Blueprint, render_template, request, jsonify
from blueprints.index import curl2py, request_, get_exp
from config.config import COOKIES_STATE_ADD, COOKIES_STATE_UPDATE, COOKIES_STATE_SUCCESS, COOKIES_STATE_DEFICIT, \
    COOKIES_STATE_OVERDUE, TYPE_WX, TYPE_QQ, COOKIES_STATE_PAUSE, COOKIES_STATE_START, COOKIES_STATE_ENDED
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
    result = CookiesLogModel.query.filter_by(account=keyword).order_by(db.text('-create_date')).all()
    result = result if result else CookiesLogModel.query.filter_by(remarks=keyword).order_by(db.text('-create_date')).all()
    data_list = []
    for i in result:
        dit = {'id': i.id, 'account': i.account, 'remarks': i.remarks, 'states': i.states,
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
        dit = {'id': i.id, 'account': i.account, 'remarks': i.remarks, 'states': i.states, 'type': i.type,
               'create_date': str(i.create_date) if i.create_date else '暂无信息', }
        data_list.append(dit)
    dic = {'code': 0, 'msg': 'SUCCESS', 'count': len(result), 'data': data_list}
    return json.dumps(dic, ensure_ascii=False)


def get_exp_voucher(keyword):
    exp, state, type_ = '未知', '未知', '未知'
    if IsNotNull(keyword):
        cookies = CookiesModel.query.filter_by(qq=keyword).first()
        cookies = cookies if cookies else CookiesModel.query.filter_by(remarks=keyword).first()
        cookies = cookies if cookies else CookiesModel.query.filter_by(account=keyword).first()
        state = cookies.states
        type_ = cookies.type
        if state != COOKIES_STATE_OVERDUE:
            result, json_data, exp = request_(cookies.account, cookies.url, cookies.headers,
                                              str(get_exp_voucher_data(eval(cookies.data), type_)))
    return exp, get_cookies_state(state), get_type(type_)


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


def get_cookies_state(CODE):
    if CODE == COOKIES_STATE_ADD:
        return '账号新增'
    elif CODE == COOKIES_STATE_UPDATE:
        return '账号更新'
    elif CODE == COOKIES_STATE_OVERDUE:
        return 'Curl过期'
    elif CODE == COOKIES_STATE_SUCCESS:
        return '兑换成功'
    elif CODE == COOKIES_STATE_DEFICIT:
        return '余额不足'
    elif CODE == COOKIES_STATE_PAUSE:
        return '暂停任务'
    elif CODE == COOKIES_STATE_START:
        return '任务重启'
    elif CODE == COOKIES_STATE_ENDED:
        return '今日发完'
    else:
        return '未知状态'


@bp.route('/AcManageAllData', methods=['GET', 'POST'])
def AcManageAllData():
    return render_template('manage.html', keyword='All')


@bp.route('/manage_data', methods=['GET', 'POST'])
def manage_data():
    keyword = request.args.get('keyword')
    if keyword == 'All':
        result = CookiesModel.query.order_by(db.text('-update_date')).all()
    else:
        result = CookiesModel.query.filter_by(account=keyword).order_by(db.text('-create_date')).all()
        result = result if result else CookiesModel.query.filter_by(remarks=keyword).order_by(
            db.text('-create_date')).all()
    data_list = []
    for i in result:
        exp, expscore = get_exp(i.account)
        dit = {'id': i.id, 'account': i.account, 'remarks': i.remarks, 'states': i.states, 'type': i.type,
               'create_date': str(i.create_date) if i.create_date else '暂无信息', 'score': expscore,
               'update_date': str(i.update_date) if i.update_date else '暂无信息', 'exp': exp}
        data_list.append(dit)
    dic = {'code': 0, 'msg': 'SUCCESS', 'count': len(result), 'data': data_list}
    return json.dumps(dic, ensure_ascii=False)


@bp.route('/account_pause', methods=['GET', 'POST'])
def account_pause():
    id_ = request.form.get('id_')
    result = CookiesModel.query.filter_by(id=id_).first()
    if result is not None:
        result.states = 106
        db.session.commit()
        return jsonify({'code': 200, 'msg': '暂停成功'})
    else:
        return jsonify({'code': 400, 'msg': '暂停失败'})


@bp.route('/account_del', methods=['GET', 'POST'])
def account_del():
    id_ = request.form.get('id_')
    result = CookiesModel.query.filter_by(id=id_).first()
    if result is not None:
        db.session.delete(result)
        db.session.commit()
        return jsonify({'code': 200, 'msg': '删除成功'})
    else:
        return jsonify({'code': 400, 'msg': '删除失败'})


@bp.route('/account_start', methods=['GET', 'POST'])
def account_start():
    id_ = request.form.get('id_')
    result = CookiesModel.query.filter_by(id=id_).first()
    if result is not None:
        result.states = 107
        db.session.commit()
        return jsonify({'code': 200, 'msg': '重启成功'})
    else:
        return jsonify({'code': 400, 'msg': '重启失败'})


@bp.route('/account_update', methods=['GET', 'POST'])
def account_update():
    if request.method == 'POST':
        id_ = request.form.get('id_')
        result = CookiesModel.query.filter_by(id=id_).first()
        curl = request.form.get('cookies')
        if IsNull(curl):
            return jsonify({'code': 400, 'msg': 'curl为空，请检查！'})
        return curl2py(curl, result.account, result.remarks)
    else:
        return jsonify({'code': 400, 'msg': '系统错误'})


@bp.route('/manage_search', methods=['GET', 'POST'])
def manage_search():
    if request.method == 'GET':
        keyword = request.args.get('keyword')
        return render_template('manage.html', keyword=keyword)
    else:
        return render_template('index.html')



