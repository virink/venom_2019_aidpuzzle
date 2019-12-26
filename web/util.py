#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
    Author : Virink <virink@outlook.com>
    Date   : 2019/11/28, 13:14
"""

import os
import sys
import random
import zipfile
import string
from PIL import Image, ImageDraw, ImageFont

TABLE = string.ascii_letters + string.digits
UPLOAD = 'tmp/'
# UPLOAD = '/app/tmp/'


def genRandStr(n=30):
    return ''.join([random.choice(TABLE) for i in range(n)])


def randPoint(w, h):
    return tuple(random.randint(0, x) for x in [w, h])


def randRGB():
    return tuple(random.randint(0, 255) for i in range(3))


def randDegree():
    return random.randint(-90, 90)


def genPuzzle(secret='test', level=0, w=43, h=30):
    # Open Image
    origin_image = 'static/origin.png'
    im = Image.open(origin_image)
    width, height = im.size

    xn = int(width/w)
    yn = int(height / h)

    dr = ImageDraw.Draw(im)
    fnt_size = 40
    fnt = ImageFont.truetype('static/monaco.ttf', 60)
    s_pos = (random.randint(10, width-(len(secret)*fnt_size-10)),
             random.randint(10, height-fnt_size-10))

    if level:
        # 干扰线
        for i in range(0, 100):
            dr.line([randPoint(width, height), randPoint(width, height)],
                    randRGB(), width=random.randint(1, 5))
            dr.arc([randPoint(width, height), randPoint(width, height)], randDegree(),
                   randDegree(), randRGB(), width=random.randint(1, 5))

        # 干扰文本
        text_num = 20
        while text_num > 0:
            _x, _y = randPoint(width, height)
            if _y > s_pos[1] + fnt_size or _y < s_pos[1] - fnt_size:
                text = genRandStr(random.randint(10, 30))
                for i in range(len(text)):
                    dr.text((_x+(fnt_size*i), _y),
                            text[i], font=fnt, fill=randRGB())
                text_num -= 1

    # Secret
    secret = "secret{%s}" % (secret)
    for i in range(len(secret)):
        dr.text((s_pos[0]+(fnt_size*i), s_pos[1]),
                secret[i], font=fnt, fill=randRGB())

    # Crop Image & Clear Image Time
    name = genRandStr(10)
    p_path = '%s/%s' % (UPLOAD, name)
    print("[D] puzzles : %s" % p_path)
    im.save('static/%s_flag.png' % name)
    print("[D] flag png : static/%s_flag.png" % name)
    try:
        os.mkdir(p_path)
    except OSError:
        pass
    for y in range(0, yn):
        for x in range(0, xn):
            crop = im.crop((x*w, y*h, (x+1) * w, (y+1)*h))
            crop.save('%s/%s.png' % (p_path, genRandStr(10)), 'PNG')
    # Mac
    os.system("cd %s && ls | xargs -n 1 touch -a -t 202011111111.11" % (p_path))
    # Linux
    # os.system("cd %s && ls | xargs -n 1 touch -d 202011111111.11" % (p_path))

    # Package Image
    os.system("zip -r %s %s > /dev/null" % (p_path + '.zip', p_path))

    # Delete Temp Puzzles
    try:
        os.removedirs(p_path)
    except OSError:
        pass
    return p_path+'.zip'


if __name__ == '__main__':
    print(genPuzzle(secret='834a8ed100e484ec0d631a7b62fffc63', level=1))
