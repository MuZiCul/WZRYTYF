from flask import Flask
from flask_apscheduler import APScheduler

from blueprints.exchange import SkinDebris, Reset
from utils.utils import send_to_wecom
from blueprints import index_bp
from config.exts import db
from flask_migrate import Migrate
import config.config as config

app = Flask(__name__)
app.config['SCHEDULER_TIMEZONE'] = 'Asia/Shanghai'

app.config.from_object(config)
db.init_app(app)
migrate = Migrate(app, db)


app.register_blueprint(index_bp)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()


@scheduler.task('cron', id='Reset', hour=0)
def Reset_():
    try:
        with scheduler.app.app_context():
            Reset()
    except Exception as e:
        send_to_wecom('体验服服务器异常，请检查！\n错误详情：'+ str(e))


@scheduler.task('interval', id='SkinDebris', minutes=30)
def SkinDebris_():
    try:
        with scheduler.app.app_context():
            SkinDebris()
    except Exception as e:
        send_to_wecom('体验服服务器异常，请检查！\n错误详情：'+ str(e))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)
