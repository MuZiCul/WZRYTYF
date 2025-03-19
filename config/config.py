# 数据库配置信息
import json
from flask_apscheduler.auth import HTTPBasicAuth

# 读取secret.json文件
with open('secret.json', 'r') as f:
    secret_config = json.load(f)

HOSTNAME = secret_config['HOSTNAME']
PORT = secret_config['PORT']
DATABASE = secret_config['DATABASE']
USERNAME = secret_config['USERNAME']
PASSWORD = secret_config['PASSWORD']
DB_URI = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(USERNAME, PASSWORD, HOSTNAME, PORT, DATABASE)
SQLALCHEMY_DATABASE_URI = DB_URI
SQLALCHEMY_TRACK_MODIFICATIONS = True
SECRET_KEY = secret_config['SECRET_KEY']

# 定时器配置
SCHEDULER_API_ENABLED = True
SCHEDULER_J0B_DEFAULTS = {
    'coalesce ': False,
    'max_instances ': 10
}
SCHEDULER_TIMEZONE = 'Asia/Shanghai'
SCHEDULER_API_PREFIX = secret_config['SCHEDULER_API_PREFIX']
SCHEDULER_AUTH = HTTPBasicAuth()

# 邮箱配置
MAIL_SERVER = secret_config['MAIL_SERVER']
MAIL_PORT = secret_config['MAIL_PORT']
MAIL_USE_TLS = secret_config['MAIL_USE_TLS']
MAIL_USE_SSL = secret_config['MAIL_USE_SSL']
MAIL_DEBUG = secret_config['MAIL_DEBUG']
MAIL_USERNAME = secret_config['MAIL_USERNAME']
MAIL_PASSWORD = secret_config['MAIL_PASSWORD']
MAIL_DEFAULT_SENDER = secret_config['MAIL_DEFAULT_SENDER']

# 企业微信配置
WECOM_CID = secret_config['WECOM_CID']  # 企业id
WECOM_AID = secret_config['WECOM_AID']  # 应用id
WECOM_SECRET = secret_config['WECOM_SECRET']  # 应用secret
WECOM_TOUID = secret_config['WECOM_TOUID']

#MT配置
WECOM_SECRET_KEY = secret_config['WECOM_SECRET_KEY']

# 日志状态配置
COOKIES_STATE_ADD = 801  # 新增
COOKIES_STATE_UPDATE = 802  # 更新
COOKIES_STATE_OVERDUE = 803  # 过期
COOKIES_STATE_SUCCESS = 804  # 成功
COOKIES_STATE_DEFICIT = 805  # 赤字
COOKIES_STATE_PAUSE = 806  # 暂停
COOKIES_STATE_START = 807  # 重启
COOKIES_STATE_ENDED = 808  # 发完

# 账号类型
TYPE_WX = 201
TYPE_QQ = 202

# server酱Key
server_key = secret_config['SERVER_KEY']

# secret.json格式如下：
# {
#     "HOSTNAME": "",
#     "PORT": "",
#     "DATABASE": "",
#     "USERNAME": "",
#     "PASSWORD": "",
#     "REDIS_HOST": "",
#     "REDIS_PORT": "",
#     "REDIS_PASSWORD": "",
#     "SECRET_KEY": "",
#     "SCHEDULER_API_PREFIX": "",
#     "MAIL_SERVER": "",
#     "MAIL_PORT": "",
#     "MAIL_USE_TLS": false,
#     "MAIL_USE_SSL": true,
#     "MAIL_DEBUG": true,
#     "MAIL_USERNAME": "",
#     "MAIL_PASSWORD": "",
#     "MAIL_DEFAULT_SENDER": "",
#     "WECOM_CID": "",
#     "WECOM_AID": "",
#     "WECOM_SECRET": "",
#     "WECOM_TOUID": "",
#     "WECOM_IP": "",
#     "WECOM_PORT": "",
#     "WECOM_INTERFACE": "",
#     "WECOM_RECIPIENT": "",
#     "WECOM_SECRET_KEY": "",
#     "SERVER_KEY": ""
# }
