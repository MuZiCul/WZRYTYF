from config.exts import db
from datetime import datetime


class CookiesModel(db.Model):
    __tablename__ = "cookies"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    qq = db.Column(db.String(100), nullable=False, unique=True)
    wx = db.Column(db.String(100), nullable=False, unique=True)
    remarks = db.Column(db.String(100))
    url = db.Column(db.String(2000), nullable=False)
    headers = db.Column(db.String(20000), nullable=False)
    data = db.Column(db.String(20000), nullable=False)
    Notifications = db.Column(db.Integer)
    contact = db.Column(db.String(100))
    type = db.Column(db.Integer)
    states = db.Column(db.Integer)
    create_date = db.Column(db.DateTime, default=datetime.now)


class CookiesLogModel(db.Model):
    __tablename__ = "cookies_log"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    qq = db.Column(db.String(100), nullable=False)
    remarks = db.Column(db.String(100))
    states = db.Column(db.Integer)
    type = db.Column(db.Integer)
    create_date = db.Column(db.DateTime, default=datetime.now)
