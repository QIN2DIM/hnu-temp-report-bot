# Author: BeiYu
# Github: https://github.com/beiyuouo
# Date  : 2021/1/8 13:28
# Description:

import base64
from json.decoder import JSONDecodeError

from nonebot.adapters.cqhttp import Message, unescape
from nonebot.matcher import Matcher
from nonebot.typing import T_State

from .alioss import AliyunOSS
from .config import *
import oss2
from datetime import datetime
import httpx
from nonebot.log import logger

import csv

USER_DIC = {}
RE_USER_DIC = {}


def init_dic():
    with open(os.path.join(PLUGINS_PATH, 'dataset/userdic.csv'), encoding='utf-8') as f:
        f_csv = csv.reader(f)
        for row in f_csv:
            qq = row[2].split('@')[0]
            stu_num = row[0]
            USER_DIC[qq] = stu_num
            RE_USER_DIC[stu_num] = qq
        logger.debug(USER_DIC)

    with open(os.path.join(PLUGINS_PATH, 'dataset/user.csv'), encoding='utf-8') as f:
        f_csv = csv.reader(f)
        for row in f_csv:
            qq = row[2].split('@')[0]
            stu_num = row[1]
            USER_DIC[qq] = stu_num
            RE_USER_DIC[stu_num] = qq
        logger.debug(USER_DIC)


init_dic()


def qq2stunum(qq: str):
    if qq in USER_DIC.keys():
        return USER_DIC[qq]
    return None


def stunum2qq(stunum: str):
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
        resp = await client.post(ALKAID_TWQD_PLUS_API, data=user)

    return resp.json()


async def tempReportEvent(at_: str, stu_num: str, macher: Matcher):
    logger.debug(f'{stu_num} 开始签到')

    # 有没有签到
    oss = AliyunOSS()
    if not oss.snp_exist(stu_num):
        # API POST JSON
        try:
            json = await get_json(stu_num)
            code = json['code']
        except JSONDecodeError:
            logger.error(NULL_PROMPT)
            if SEND_LOG:
                macher.send(Message(NULL_PROMPT))
            return

        logger.debug(f'已获得json: {json}')

        info = osh_status_code[int(code)]
        logger.debug(f'{info}')
        # CODE
        if code == CODE_SUCCESS:
            msg = Message(at_ + SUCCESS_PROMPT)
            await macher.send(msg)
        elif code == CODE_FAILED:
            msg = Message(at_ + FAILED_PROMPT)
            await macher.send(msg)
            return
        elif code == CODE_PERMISSION_ERROR:
            msg = Message(at_ + PERMISSION_ERROR_PROMPT)
            await macher.send(msg)
            return

    logger.debug('oss上已存在信息')

    # 从OSS下载文件
    resp = await oss.download_snp(stu_num)
    if not resp:
        msg = Message(at_ + DOWNLOAD_FAILED_PROMPT)
        await macher.send(msg)
        return

    logger.debug('截图下载成功')

    txt_path = SERVER_DIR_SCREENSHOT + f"/{stu_num}.txt"
    img_path = await conv_file(txt_path)

    logger.debug('截图转换成功，准备发送！')

    # reply = Message("[CQ:at,qq={}] [CQ:image,file={}]".format(user_id, img_path))
    # await macher.send(Message(unescape("[CQ:image,file=20181620310156.png]")))
    # logger.debug('image_path: {}'.format(img_path))
    reply = Message(unescape("[CQ:image,file={}]".format(img_path)))
    await macher.send(reply)


async def addUserEvent(state: T_State):
    username = state['username']
    password = state['password']
    email = state['email']
    user_ = {
        'school': '海南大学',
        'username': username,
        'password': password,
    }
    logger.debug(f'addUserEvent called: {user_}')

    async with httpx.AsyncClient() as client:
        resp = await client.post(ADDUSER_VERITY_EXIST_API, data=user_)
        logger.debug(f'resp exist: {resp}')

        # 若账号可登记则继续执行
        if resp.json()['msg'] == 'success':
            logger.debug(">> 账号可登记")
        else:
            return CODE_ADDUSER_ACCOUNT_EXIST

        # 2.验证账号是否正确
        res_account = await client.post(ADDUESR_VERITY_ACCOUNT_API, data=user_)
        logger.debug(f'res_account: {res_account}')

        # 若账号信息无误则继续执行
        if res_account.json()['msg'] == 'success':
            logger.debug(">> 账号信息正确")
        else:
            return CODE_ADDUSER_ACCOUNT_ERROR

        # 3.验证邮箱 -> if success response token
        user_.update({'email': email})
        res_email = await client.post(ADDUESR_VERITY_EMAIL_API, data=user_)
        logger.debug(f'res_email: {res_email}')

        if res_email.json()['msg'] == 'success':
            user_.update({'token': res_email.json()['token']})
            state['token'] = res_email.json()['token']
            logger.debug(f"token: {res_email.json()['token']}")
        else:
            return CODE_ADDUSER_EMAIL_ERROR

        res_post_code = await client.post(ADDUSER_VERITY_CODE_API, data=user_)
        logger.debug(f'res_post{res_post_code}')
        if res_post_code.json()['msg'] == 'success':
            logger.debug('>> 邮箱验证码已发送 请注意查收')
            return CODE_ADDUSER_EMAIL_SEND


async def verifySid(state: T_State):
    user_ = {
        'school': '海南大学',
        'username': state['username'],
        'password': state['password'],
        'email': state['email'],
        'token': state['token'],
        'sid': state['sid'],
    }
    logger.debug(f'verifySidEvent called: {user_}')

    async with httpx.AsyncClient() as client:
        res_add = await client.post(ADDUSER_ADDUSER_API, data=user_)
        logger.debug(f'res_add: {res_add}')
        if res_add.json()['msg'] == 'success':
            # 账号入库成功，若此项success 再次执行提交程序 应返回failed 并提示账号已登记
            logger.log(res_add.json()['info'])
            return CODE_ADDUSER_SUCCESS
        else:
            return CODE_ADDUSER_SID_ERROR
