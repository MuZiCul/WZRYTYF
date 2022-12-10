from config.exts import db
from datetime import datetime


class CookiesModel(db.Model):
    __tablename__ = "cookies"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    qq = db.Column(db.String(50), nullable=False, unique=True)
    url = db.Column(db.String(2000), nullable=False)
    headers = db.Column(db.String(20000), nullable=False)
    data = db.Column(db.String(20000), nullable=False)
    past_due = db.Column(db.Integer, nullable=False)
    convertibility = db.Column(db.Integer, nullable=False)
    create_date = db.Column(db.DateTime, default=datetime.now)
