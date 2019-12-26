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
from flask import Flask, session, send_file, render_template, redirect, request
from flask_session import Session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from db import db, Ranks, addRanks
from util import genPuzzle, genRandStr


pool = redis.ConnectionPool(host='127.0.0.1', port=6379, max_connections=10)
rds = redis.Redis(db=2, connection_pool=pool, decode_responses=True)

EASY_TIME = 3600
HELL_TIME = 600 + 100


def create_app():
    app = Flask(__name__)

    app.secret_key = 'hjaie234uhvila234tefweh3452kuvyh234ased'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    db.init_app(app)
    Session(app)

    return app


app = create_app()

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["5 per minute"],
    storage_uri="redis://127.0.0.1:6379",
    headers_enabled=True,
    key_prefix="limit_"
)


@app.before_first_request
def create_tables():
    db.create_all()


@app.route('/', methods=['GET'])
@limiter.exempt
def index():
    easy_ranks = Ranks.query.filter_by(level=0).order_by(Ranks.time).group_by(
        Ranks.name).limit(100).all()
    hell_ranks = Ranks.query.filter_by(level=1).order_by(Ranks.time).group_by(
        Ranks.name).limit(100).all()
    print(easy_ranks)
    print(hell_ranks)
    name = session.get('name', False)
    msg = session.get('msg', "")
    session['msg'] = ""
    return render_template('index.html', easy_ranks=easy_ranks, hell_ranks=hell_ranks, name=name, msg=msg, t=time.time())


@app.route('/login', methods=['POST'])
@limiter.exempt
def login():
    username = request.form.get("username", "")
    if username:
        session['name'] = username
    return redirect("/")


@app.route('/logout', methods=['GET'])
@limiter.exempt
def logout():
    session['name'] = False
    return redirect("/")


@app.route('/download/easy', methods=['GET'])
@limiter.limit("10 per hour")
def download_easy():
    secret = genRandStr()
    flag = "easy|%s" % genRandStr()
    print("[D] Secret : %s" % secret)
    print("[D] Flag   : %s" % flag)
    # Gen Puzzles
    print("[+] Start gen puzzle...")
    _t = time.time()
    fn = genPuzzle(secret=secret, level=0)
    print("[+] Puzzle name : %s" % fn)
    print("[+] Use time: %d" % (time.time() - _t))
    rds.setex(secret, EASY_TIME, flag)
    if fn:
        return send_file(fn, as_attachment=True, cache_timeout=1, conditional=True)
    else:
        return 'Error'


@app.route('/download/hell', methods=['GET'])
@limiter.limit("10 per hour")
def download_hell():
    secret = genRandStr()
    flag = "hell|%s" % (genRandStr())
    print("[D] Secret : %s" % secret)
    print("[D] Flag   : %s" % flag)
    # Gen Puzzles
    print("[+] Start gen puzzle...")
    _t = time.time()
    fn = genPuzzle(secret=secret, level=1)
    print("[+] Puzzle name : %s" % fn)
    print("[+] Use time: %d" % (time.time() - _t))
    rds.setex(secret, HELL_TIME, flag)
    if fn:
        return send_file(fn, as_attachment=True, cache_timeout=1, conditional=True)
    else:
        return 'Error'


@app.route('/secret', methods=['POST'])
def secret():
    username = session['name'] or False
    if username:
        s = request.form.get("secret", "")
        flag = rds.get(s)
        if s and flag:
            flag = flag.decode('utf-8')
            t = rds.ttl(s)
            print("[D] %s > %s : %s - %d" % (username, s, flag, t))
            if flag.startswith("easy"):
                addRanks(username, EASY_TIME - t, 0)
            elif flag.startswith("hell"):
                addRanks(username, HELL_TIME - t, 1)
            rds.delete(s)
            session['msg'] = "flag is %s" % flag[5:]
        else:
            session['msg'] = "Error or Timeout!!!"
    else:
        session['msg'] = 'Not Login!'
    return redirect("/")


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
    # genPuzzle()
    # print(genPuzzle(secret='834a8ed100e484ec0d631a7b62fffc63', w=43, h=30))
