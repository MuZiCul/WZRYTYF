from config.exts import db
from datetime import datetime


class CookiesModel(db.Model):
    __tablename__ = "cookies"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    qq = db.Column(db.String(100), nullable=False, unique=True)
    account = db.Column(db.String(100), nullable=False, unique=True)
    remarks = db.Column(db.String(100))
    url = db.Column(db.String(2000), nullable=False)
    headers = db.Column(db.String(20000), nullable=False)
    data = db.Column(db.String(20000), nullable=False)
    data1 = db.Column(db.String(20000), nullable=False)
    Notifications = db.Column(db.Integer)
    contact = db.Column(db.String(100))
    type = db.Column(db.Integer)
    states = db.Column(db.Integer)
    warn = db.Column(db.Integer)
    create_date = db.Column(db.DateTime, default=datetime.now)
    update_date = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class CookiesLogModel(db.Model):
    __tablename__ = "cookies_log"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    account = db.Column(db.String(100), nullable=False)
    remarks = db.Column(db.String(100))
    exp = db.Column(db.String(100))
    states = db.Column(db.Integer)
    type = db.Column(db.Integer)
    create_date = db.Column(db.DateTime, default=datetime.now)


class UpdateLogModel(db.Model):
    __tablename__ = "update_log"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    update_date = db.Column(db.String(100))
    update_id = db.Column(db.String(100))
    url = db.Column(db.String(100))
    create_date = db.Column(db.DateTime, default=datetime.now)


class ArgumentsModel(db.Model):
    __tablename__ = "arguments"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    value = db.Column(db.String(100))
