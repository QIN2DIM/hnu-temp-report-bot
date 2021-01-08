# Author: BeiYu
# Github: https://github.com/beiyuouo
# Date  : 2021/1/8 13:03
# Description:
from json.decoder import JSONDecodeError

from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp import Bot, unescape, MessageEvent, Message, MessageSegment
from nonebot.log import logger

from .config import *
from .utils import *
from .alioss import *

twqd = on_command("twqd", rule=to_me(), priority=5)


@twqd.handle()
async def handle(bot: Bot, event: Event, state: T_State):
    # print(event.get_event_name().split(".")[1])

    if not ENABLE_PRIVATE and event.get_event_name().split(".")[1] != "group":
        await twqd.finish(Message(PRIVATE_PROMPT))

    args = str(event.get_message()).strip()
    if args:
        state["stu_nums"] = args


@twqd.got("stu_nums", prompt=ARGS_PROMPT)
async def handle_event(bot: Bot, event: Event, state: T_State):
    logger.debug('准备执行twqd')

    stu_nums = str(state["stu_nums"]).split()
    user_id = event.get_user_id()
    at_ = "[CQ:at,qq={}]".format(user_id)
    for stu_num in stu_nums:
        # TODO: stu_num check
        await tempReportEvent(at_, stu_num, twqd)


twqdall = on_command("twqdall", rule=to_me(), priority=5, permission=SUPERUSER)


@twqdall.handle()
async def handle(bot: Bot, event: Event, state: T_State):
    if not ENABLE_PRIVATE and event.get_event_name().split(".")[1] != "group":
        await twqdall.finish(Message(PRIVATE_PROMPT))

    logger.debug(f'session id: {event.get_session_id()}')
    logger.debug(f'event description: {event.get_event_description()}')
    # event description: Message -639288931 from 729320011@[群:1001320858] ""
    group_id = str(event.dict()['group_id'])
    logger.debug(f'group id {group_id}')
    if SEND_LOG:
        await twqdall.send(Message(group_id))

    # Get All User
    group_member_list = await bot.get_group_member_list(group_id=group_id)
    logger.debug(group_member_list)
    if SEND_LOG:
        await twqdall.send(Message(str(group_member_list)))

    # Map User
    for member in group_member_list:
        user_id = str(member['user_id'])
        logger.debug(f'processing: {user_id}')
        at_ = "[CQ:at,qq={}]".format(user_id)
        if SEND_LOG:
            await twqdall.send(Message(at_ + TWQDALL_RUNNING_PROMPT))

        stu_num = await qq2stunum(user_id)
        logger.debug(f'will process: {user_id} {stu_num}')

        if SEND_LOG:
            await twqdall.send(Message(at_ + TWQDALL_RUNNING_PROMPT + f'{stu_num}'))

        if not stu_num:
            await twqdall.send(Message(at_ + TWQDALL_NOT_IN_DATASET_PROMPT))
            continue

        await tempReportEvent(at_, stu_num, twqdall)

    await twqdall.finish(Message(TWQDALL_SUCCESS_PROMPT))


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

        logger.debug(f'已获得json: {json}')

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


# Add User Event

adduser = on_command("adduser", rule=to_me(), priority=5, permission=SUPERUSER)


@adduser.handle()
async def handle(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip()
    if args:
        state["args"] = args


@adduser.got("args", prompt=ARGS2_PROMPT)
async def handle(bot: Bot, event: Event, state: T_State):
    args = str(state["args"]).split()
    try:
        username, password, email = args
    except Exception:
        adduser.finish(Message(ADDUSER_ARGS_PROMPT))

    logger.debug(f'adduser: {username} {password} {email}')
    await adduserEvent(username, password, email)


async def adduserEvent(username: str, password: str, email: str):
    pass


# Query Event

query = on_command("query", rule=to_me(), priority=5, permission=SUPERUSER)


@query.handle()
async def handle(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip()
    if args:
        state["args"] = args


@query.got("args", prompt=QUERY_ARGS_PROMPT)
async def handle(bot: Bot, event: Event, state: T_State):
    user_id = event.get_user_id()
    at_ = "[CQ:at,qq={}]".format(user_id)
    args = str(state["args"]).split()
    if len(args) != 2:
        await query.finish(Message(QUERY_ARGS_PROMPT))

    type, key = args
    logger.debug(f'query: {type} {key}')
    if type == '学号':
        qq = await stunum2qq(key)
        if not qq:
            await query.finish(Message(at_ + QUERY_NO_DATA_PROMPT))
        else:
            await query.finish(Message(at_ + QUERY_DATA_FORMAT.format(key, qq)))
    elif str(type).lower() == 'qq':
        stunum = await qq2stunum(key)
        if not stunum:
            await query.finish(Message(at_ + QUERY_NO_DATA_PROMPT))
        else:
            await query.finish(Message(at_ + QUERY_DATA_FORMAT.format(stunum, key)))
    else:
        await query.finish(Message(QUERY_NO_SUCH_TYPE_PROMPT))
