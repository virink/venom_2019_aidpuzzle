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
import hashlib
from PIL import Image, ImageDraw, ImageFont

TABLE = string.ascii_letters + string.digits
PUZZLES = 'tmp/'


def md5(s):
    m = hashlib.md5()
    m.update(s.encode(encoding='UTF-8'))
    return m.hexdigest()


def genRandStr(n=30):
    return ''.join([random.choice(TABLE) for i in range(n)])


def randPoint(w, h):
    return tuple(random.randint(0, x) for x in [w, h])


def randRGB():
    return tuple(random.randint(0, 255) for i in range(3))


def randDegree():
    return random.randint(-90, 90)


def genPuzzle(filename, secret="", w=32, h=20):
    # Open Image
    origin_image = 'aidpuzzle.png'
    im = Image.open(origin_image)
    width, height = im.size
    xn = int(width / w)
    yn = int(height / h)
    dr = ImageDraw.Draw(im)

    # 干扰线
    # for i in range(0, 100):
    #     dr.line([randPoint(width, height), randPoint(width, height)],
    #             randRGB(), width=random.randint(1, 5))
    #     dr.arc([randPoint(width, height), randPoint(width, height)], randDegree(),
    #            randDegree(), randRGB(), width=random.randint(1, 5))

    # Secret
    secret = "secret{%s}" % (secret)
    fnt_size = 150
    # 2560 - 1600
    fnt = ImageFont.truetype('monaco.ttf', fnt_size)
    top = random.randint(100, 200)
    for j in range(5):
        left = random.randint(100, width-100-(8*fnt_size))
        for i in range(8):
            dr.text((left+(fnt_size*i), top+j*300),
                    secret[j*8+i], font=fnt, fill=randRGB())

    # Crop Image & Clear Image Time
    # ./tmp/{filename}
    p_path = '%s/%s' % (PUZZLES, filename)
    im.save('%s_flag.png' % p_path)
    # ./tmp/{filename}_flag.png
    print("[D] flag png : %s_flag.png" % p_path)

    # Crop Image
    try:
        os.mkdir(p_path)
    except OSError:
        pass
    for y in range(0, yn):
        for x in range(0, xn):
            crop = im.crop((x * w, y * h, (x + 1) * w, (y + 1) * h))
            # ./tmp/filename/{genRandStr}.png
            crop.save('%s/%s.png' % (p_path, genRandStr(10)), 'PNG')
    # Mac
    os.system("cd %s && ls | xargs -n 1 touch -a -t 202011111111.11" % (p_path))
    # Linux
    # os.system("cd %s;touch -d '2019-12-25 08:00:00' *" % (p_path))

    # Package Image
    # ./tmp/filename.zip
    os.system("cd tmp; zip -r %s %s > /dev/null" %
              (filename + '.zip', filename))

    # Delete Temp Puzzles
    # os.system('rm -rf %s' % p_path)
    # return p_path+'.zip'


if __name__ == '__main__':
    try:
        os.mkdir("tmp")
    except OSError:
        pass

    filename = 'easyx'
    secret = md5("Venom_AID_Puzzle_%s" % filename)
    genPuzzle(filename=filename, secret=secret, w=16, h=10)

    # for i in range(256):
    #     print(i)
    #     filename = md5("Venom_AID_Puzzle_%d" % i)
    #     secret = md5("Venom_AID_Puzzle_%s" % filename)
    #     genPuzzle(filename=filename, secret=secret, level=0)
