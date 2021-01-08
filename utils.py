# Author: BeiYu
# Github: https://github.com/beiyuouo
# Date  : 2021/1/8 13:28
# Description:

import base64
from .config import *
import oss2
from datetime import datetime
import httpx
from nonebot.log import logger

import csv

USER_DIC = {}
RE_USER_DIC = {}


def init_dic():
    with open(os.path.join(PLUGINS_PATH, 'dataset/userdic.csv')) as f:
        f_csv = csv.reader(f)
        for row in f_csv:
            qq = row[2].split('@')[0]
            stu_num = row[0]
            USER_DIC[qq] = stu_num
            RE_USER_DIC[stu_num] = qq
        logger.debug(USER_DIC)

    with open(os.path.join(PLUGINS_PATH, 'dataset/user.csv')) as f:
        f_csv = csv.reader(f)
        for row in f_csv:
            qq = row[2].split('@')[0]
            stu_num = row[1]
            USER_DIC[qq] = stu_num
            RE_USER_DIC[stu_num] = qq
        logger.debug(USER_DIC)


init_dic()


async def qq2stunum(qq: str):
    if qq in USER_DIC.keys():
        return USER_DIC[qq]
    return None


async def stunum2qq(stunum: str):
    if stunum in RE_USER_DIC.keys():
        return RE_USER_DIC[stunum]
    return None


async def conv_file(path: str):
    new_path = path.split(".")[0] + ".png"

    with open(path, "r") as f:
        imgdata = base64.b64decode(f.read())
        file = open(new_path, 'wb')
        file.write(imgdata)
        file.close()
    return os.path.join(TWQD_DIR_NAME, new_path.split('/')[-1])


async def get_json(username: str):
    user = {
        'username': username
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(ALKAID_POST_API, data=user)

    return resp.json()

