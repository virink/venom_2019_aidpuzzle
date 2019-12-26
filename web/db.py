#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
    Author : Virink <virink@outlook.com>
    Date   : 2019/11/28, 13:14
"""
import time as time
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class Users(db.Model):

    __tablename__ = 'users'
    __table_args__ = {
        'mysql_charset': 'utf8'     # 指定表的编码格式
    }

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    qq = db.Column(db.String(80), unique=True)
    download1 = db.Column(db.Integer, default=0)
    submit1 = db.Column(db.Integer, default=0)
    download2 = db.Column(db.Integer, default=0)
    submit2 = db.Column(db.Integer, default=0)
    download3 = db.Column(db.Integer, default=0)
    submit3 = db.Column(db.Integer, default=0)

    def __repr__(self):
        return 'Rank : %s' % self.name
