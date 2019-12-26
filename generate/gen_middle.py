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
PUZZLES = 'tmp'


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


def randFlag():
    tables = ['flag', 'venom', 'Line', 'ChaMD5']
    return "%s{%s}" % (random.choice(tables), md5(genRandStr()))


def genPuzzle(filename, secret="", w=32, h=20):

    secret = "secret{%s}" % (secret)
    # Open Image
    origin_image = 'aidpuzzle.png'
    im = Image.open(origin_image)
    width, height = im.size

    xn = int(width / w)
    yn = int(height / h)

    dr = ImageDraw.Draw(im)

    fnt_size = 30
    fnt = ImageFont.truetype('monaco.ttf', 40)
    s_pos = (random.randint(20, width-20-len(secret)*fnt_size),
             random.randint(20, height-fnt_size-20))

    # 干扰线
    for i in range(0, 100):
        dr.line([randPoint(width, height), randPoint(width, height)],
                randRGB(), width=random.randint(3, 6))
        dr.arc([randPoint(width, height), randPoint(width, height)], randDegree(),
               randDegree(), randRGB(), width=random.randint(3, 6))

    # 干扰文本
    text_num = 20
    while text_num > 0:
        text = randFlag()
        _x = random.randint(10, width-10-len(text)*fnt_size)
        _y = random.randint(10, height-fnt_size-10)
        # _x, _y = randPoint(x, y)
        if _y > s_pos[1] + fnt_size or _y < s_pos[1] - fnt_size:
            for i in range(len(text)):
                dr.text((_x+(fnt_size*i), _y),
                        text[i], font=fnt, fill=randRGB())
            text_num -= 1

    # Secret
    for i in range(len(secret)):
        dr.text((s_pos[0]+(fnt_size*i), s_pos[1]),
                secret[i], font=fnt, fill=randRGB())

    # Crop Image & Clear Image Time
    # ./tmp/{filename}
    p_path = '%s/%s' % (PUZZLES, filename)
    im.save('%s_flag.png' % p_path)
    # ./tmp/{filename}_flag.png
    print("[D] flag png : %s_flag.png" % p_path)

    # sys.exit(0)

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
    # os.system("cropd %s && ls | xargs -n 1 touch -a -t 202011111111.11" % (p_path))
    # Linux
    # os.system("cd %s;touch -d '2019-12-25 08:00:00' *" % (p_path))

    # Package Image
    # ./tmp/filename.zip
    os.system("cd %s; zip -r %s %s > /dev/null" %
              (PUZZLES, filename + '.zip', filename))

    # Delete Temp Puzzles
    # os.system('rm -rf %s' % p_path)
    print("[+] Success")


if __name__ == '__main__':
    try:
        os.mkdir(PUZZLES)
    except OSError:
        pass

    # filename = md5("Venom_AID_Puzzle")
    filename = 'middle'
    secret = md5("Venom_AID_Puzzle_%s" % filename)
    genPuzzle(filename=filename, secret=secret)
    # for i in range(256):
    #     print(i)
    #     filename = md5("Venom_AID_Puzzle_%d" % i)
    #     secret = md5("Venom_AID_Puzzle_%s" % filename)
    #     genPuzzle(filename=filename, secret=secret)
