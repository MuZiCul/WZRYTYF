from flask import Flask, redirect, url_for
from flask_apscheduler import APScheduler

from blueprints.exchange import SkinDebris, CheckWZRY
from utils.utils import send_to_wecom
from blueprints import index_bp, search_bp
from config.exts import db
from flask_migrate import Migrate
import config.config as config

app = Flask(__name__)
app.config['SCHEDULER_TIMEZONE'] = 'Asia/Shanghai'

app.config.from_object(config)
db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(index_bp)
app.register_blueprint(search_bp)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()


@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='images/logo.ico'))


@scheduler.task('interval', id='SkinDebris', hours=3)
def SkinDebris_():
    try:
        with scheduler.app.app_context():
            SkinDebris()
    except Exception as e:
        send_to_wecom('体验服兑换服务器异常，请检查！\n错误详情：' + str(e))


@scheduler.task('interval', id='CheckWZRY', hours=1)
def CheckWZRY_():
    try:
        with scheduler.app.app_context():
            CheckWZRY()
    except Exception as e:
        send_to_wecom('体验服更新服务器异常，更新检测异常，请检查！\n错误详情：' + str(e))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)
