from flask import Flask
from flask_apscheduler import APScheduler

from blueprints.exchange import SkinDebris, check_cookies
from config.config import cookies1, params1, data1, cookies, params, data, cookies0, params0, data0
from utils.utils import send_to_wecom

app = Flask(__name__)
app.config['SCHEDULER_TIMEZONE'] = 'Asia/Shanghai'
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@scheduler.task('cron', id='QQ', hour=1)
def SkinDebris_():
    try:
        SkinDebris(params, cookies, data)
        SkinDebris(params1, cookies1, data1)
        SkinDebris(params0, cookies0, data0)
    except Exception as e:
        send_to_wecom('体验服服务器异常，请检查！\n错误详情：'+ str(e))


@scheduler.task('interval', id='QQ_G', minutes=30)
def check_cookies_():
    try:
        check_cookies(params, cookies, data)
        check_cookies(params1, cookies1, data1)
        check_cookies(params0, cookies0, data0)
    except Exception as e:
        send_to_wecom('体验服服务器异常，请检查！\n错误详情：'+ str(e))


if __name__ == '__main__':
    app.run()
