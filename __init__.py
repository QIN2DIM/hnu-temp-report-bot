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

twqd = on_command("twqd", rule=to_me(), priority=1,
                  aliases=set(['体温签到', '签到']))


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


twqdall = on_command("twqdall", rule=to_me(), priority=1, permission=SUPERUSER)


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
    db = pymysql.connect(host=QQMAP_HOST, port=3306, user=QQMAP_USERNAME,
                         passwd=QQMAP_PASSWORD, db="cpds_db", charset='utf8')

    cursor = db.cursor()
    for member in group_member_list:
        user_id = str(member['user_id'])
        logger.debug(f'processing: {user_id}')
        at_ = "[CQ:at,qq={}]".format(user_id)
        if SEND_LOG:
            await twqdall.send(Message(at_ + TWQDALL_RUNNING_PROMPT))

        stu_num = await qq2stunum(user_id, cursor)
        logger.debug(f'will process: {user_id} {stu_num}')

        if not stu_num:
            # await twqdall.send(Message(at_ + TWQDALL_NOT_IN_DATASET_PROMPT))
            continue

        # await twqdall.send(Message(at_ + TWQDALL_RUNNING_PROMPT + f'{stu_num}'))
        await twqdall.send(Message(at_ + TWQDALL_RUNNING_PROMPT))
        await tempReportEvent(at_, stu_num, twqdall)

    db.close()
    cursor.close()
    await twqdall.finish(Message(TWQDALL_SUCCESS_PROMPT))



# Add User Event

adduser = on_command("adduser", rule=to_me(), priority=1, permission=SUPERUSER,
                     aliases=set(['添加', '添加用户']))


@adduser.handle()
async def handle(bot: Bot, event: Event, state: T_State):
    logger.debug('adduser called')
    args = str(event.get_message()).strip()
    if args:
        state["args"] = args


@adduser.got("args", prompt=ADDUSER_ARGS_PROMPT)
async def handle(bot: Bot, event: Event, state: T_State):
    args = str(state["args"]).split()
    if len(args) != 3:
        await adduser.finish(Message(ADDUSER_ARGS_PROMPT))

    username, password, email = args
    logger.debug(f'adduser: {username} {password} {email}')
    state['username'] = username
    state['password'] = password
    state['email'] = email
    code = await addUserEvent(state)
    if code == CODE_ADDUSER_ACCOUNT_EXIST:
        await adduser.finish(Message(ADDUSER_ACCOUNT_EXIST_PROMPT))
    elif code == CODE_ADDUSER_ACCOUNT_ERROR:
        await adduser.finish(Message(ADDUSER_ACCOUNT_ERROR_PROMPT))
    elif code == CODE_ADDUSER_EMAIL_ERROR:
        await adduser.finish(Message(ADDUSER_EMAIL_ERROR_PROMPT))
    elif code == CODE_ADDUSER_TOKEN_ERROR:
        await adduser.finish(Message(ADDUSER_TOKEN_ERROR_PROMPT))
    else:
        await adduser.send(Message(ADDUSER_SID_PROMPT))


@adduser.got("sid", prompt=ADDUSER_SID_PROMPT)
async def handle(bot: Bot, event: Event, state: T_State):
    code = verifySid(state)
    if code == CODE_ADDUSER_SID_ERROR:
        await adduser.finish(Message(ADDUSER_SID_ERROR_PROMPT))
    else:
        # TODO: 添加到本地数据库
        await adduser.finish(Message(CODE_ADDUSER_SUCCESS))


# Query Event

query = on_command("query", rule=to_me(), priority=1, permission=SUPERUSER,
                   aliases=set(['查询用户']))


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
    db = pymysql.connect(host=QQMAP_HOST, port=3306, user=QQMAP_USERNAME,
                         passwd=QQMAP_PASSWORD, db="cpds_db", charset='utf8')

    cursor = db.cursor()
    type, key = args
    logger.debug(f'query: {type} {key}')
    if type == '学号':
        qq = await stunum2qq(key, cursor)
        if not qq:
            await query.finish(Message(at_ + QUERY_NO_DATA_PROMPT))
        else:
            await query.finish(Message(at_ + QUERY_DATA_FORMAT.format(key, qq)))
    elif str(type).lower() == 'qq':
        stunum = await qq2stunum(key, cursor)
        if not stunum:
            await query.finish(Message(at_ + QUERY_NO_DATA_PROMPT))
        else:
            await query.finish(Message(at_ + QUERY_DATA_FORMAT.format(stunum, key)))
    else:
        await query.finish(Message(QUERY_NO_SUCH_TYPE_PROMPT))
    db.close()
    cursor.close()


# Add To MySQL
add = on_command("add", rule=to_me(), priority=1, permission=SUPERUSER)


@add.handle()
async def handle(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip()
    if args:
        state["args"] = args


@add.got("args", prompt=ADD_ARGS_PROMPT)
async def handle(bot: Bot, event: Event, state: T_State):
    user_id = event.get_user_id()
    at_ = "[CQ:at,qq={}]".format(user_id)
    args = str(state["args"]).split()
    if len(args) == 1:
        await addEvent(user_id, args[0], add)
    elif len(args) == 2:
        await addEvent(args[0], args[1], add)
    else:
        await add.finish(Message(ADD_ARGS_PROMPT))
