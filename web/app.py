#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
    Author : Virink <virink@outlook.com>
    Date   : 2019/11/28, 13:14
"""

import os
import sys
import random
import string
import time
import zipfile
import redis
from datetime import timedelta
from flask import Flask, session, send_file, render_template, redirect, request, jsonify
from flask_session import Session
from flask_limiter import Limiter

from db import db, Users
from puzzles import puzzles


pool = redis.ConnectionPool(host='127.0.0.1', port=6379, max_connections=10)
rds = redis.Redis(db=2, connection_pool=pool, decode_responses=True)

FLAG = 'flag{d8f367360ca66344c78b61638bdd22}'


def create_app():
    app = Flask(__name__)
    app.secret_key = 'hjaie234uhvila234tefweh3452kuvyh234ased'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = '/tmp/flask_session'
    app.config['SESSION_USE_SIGNER'] = True
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://aidpuzzle:aidpuzzle666@localhost:3306/aidpuzzle?charset=utf8'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    db.init_app(app)
    Session(app)
    return app


app = create_app()


def get_remote_address():
    """
    :return: the ip address for the current request (or 127.0.0.1 if none found)
    """
    return request.headers.get("X-Real-IP")


limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["10 per minute"],
    storage_uri="redis://127.0.0.1:6379",
    headers_enabled=True,
    key_prefix="limit_"
)


@app.before_first_request
def create_tables():
    db.create_all()


@app.template_filter('strftime')
def _jinja2_filter_datetime(time_stamp, fmt="%Y-%m-%d %H:%M:%S"):
    return time.strftime(fmt, time.localtime(time_stamp))


@app.route('/', methods=['GET'])
@limiter.exempt
def index():
    name = session.get('name', False)
    qq = session.get('qq', False)
    msg = session.get('msg', "")
    session['msg'] = ""
    return render_template('index.html',  name=name, qq=qq, msg=msg, t=time.time())


@app.route('/ranks', methods=['GET'])
@limiter.exempt
def ranks():
    # us = Users.query.filter(Users.submit1 != 0, Users.download1 != 0).all()
    # # SELECT name,(submit1-download1) as a,(submit2-download2) as b,(submit3-download3) as c, from users;
    sql = """SELECT name,submit1,download1,submit2,download2,submit3,download3 from users;"""
    us = db.session.execute(sql)
    res = []
    for u in us:
        a = u['submit1'] - u['download1']
        b = u['submit2'] - u['download2']
        c = u['submit3']-u['download3']
        if a <= 0:
            a = 9999999
        if b <= 0:
            b = 9999999
        if c <= 0:
            c = 9999999
        best = min(a, b, c)
        if best == a:
            s = u['submit1']
            d = u['download1']
        elif best == b:
            s = u['submit2']
            d = u['download2']
        else:
            s = u['submit3']
            d = u['download3']
        res.append({"name": u['name'], 'best': best,
                    'download': d, 'submit': s})
    res.sort(key=lambda u: u["best"])
    return render_template('ranks.html', ranks=res)


@app.route('/rules', methods=['GET'])
@limiter.exempt
def rules():
    return render_template('rules.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form.get("username", "")
    qq = request.form.get("qq", "")
    if username and qq:
        user = Users.query.filter_by(name=username).first()
        while not user:
            u = Users(name=username, qq=qq)
            db.session.add(u)
            db.session.commit()
            user = Users.query.filter_by(name=username).first()
        session['name'] = username
        session['qq'] = user.qq
        session['id'] = user.id
    return redirect("/")


@app.route('/logout', methods=['GET'])
def logout():
    session['name'] = False
    session['id'] = False
    return redirect("/")


@app.route('/geturl', methods=['GET'])
def geturl():
    qq = session.get('qq', False)
    if not qq:
        return jsonify(status=1, msg="pzl,login")
    uid = session.get('id', False)
    user = Users.query.filter_by(qq=qq).first()
    if user.submit1 == 0:
        if user.download1 == 0:
            user.download1 = time.time()
            db.session.commit()
        puzzle = puzzles[int(qq) % 256]
    elif user.submit2 == 0:
        if user.download2 == 0:
            user.download2 = time.time()
            db.session.commit()
        puzzle = puzzles[(int(qq)+100) % 256]
    elif user.submit3 == 0:
        if user.download3 == 0:
            user.download3 = time.time()
            db.session.commit()
        puzzle = puzzles[(int(qq)+200) % 256]
    else:
        return jsonify(status=1, msg="You don't have chances")
    return jsonify(status=0, url=puzzle['url'])


@app.route('/submit', methods=['POST'])
def submits():
    qq = session.get('qq', False)
    if qq:
        secret = request.form.get("secret", "")
        user = Users.query.filter_by(qq=qq).first()
        if user.submit1 == 0:
            puzzle = puzzles[int(qq) % 256]
            if secret == puzzle["secret"]:
                user.submit1 = time.time()
                db.session.commit()
                session['msg'] = 'Good Job! %s' % FLAG
        elif user.submit2 == 0:
            puzzle = puzzles[(int(qq)+100) % 256]
            if secret == puzzle["secret"]:
                user.submit2 = time.time()
                db.session.commit()
                session['msg'] = 'Good Job! %s' % FLAG
        elif user.submit3 == 0:
            puzzle = puzzles[(int(qq)+200) % 256]
            if secret == puzzle["secret"]:
                user.submit3 = time.time()
                db.session.commit()
                session['msg'] = 'Good Job! %s' % FLAG
        else:
            session['msg'] = "You don't have chances"
    else:
        session['msg'] = 'Not Login!'
    return redirect("/")


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
