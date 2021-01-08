# Author: BeiYu
# Github: https://github.com/beiyuouo
# Date  : 2021/1/8 13:04
# Description:

import pytz
import os

TIME_ZONE_CN = pytz.timezone('Asia/Shanghai')
TWQD_DIR_NAME = 'twqd'
IMAGE_DIR = 'data/images'
GOCQ_PATH = '/root/chatbot'
SERVER_DIR_SCREENSHOT = os.path.join(GOCQ_PATH, IMAGE_DIR, TWQD_DIR_NAME)
PLUGINS_PATH = 'awesome_bot/plugins/twqd'

CODE_SUCCESS = 200
CODE_FAILED = 102
CODE_PERMISSION_ERROR = 101

ENABLE_PRIVATE = False

PRIVATE_PROMPT = "别偷偷给我发消息呦~"
ARGS_PROMPT = "后面要加一个学号哟~"
ARGS2_PROMPT = "后面要加学号和密码哟~"
NULL_PROMPT = "接口异常"
SUCCESS_PROMPT = "签到成功啦！"
FAILED_PROMPT = "签到失败啦！"
PERMISSION_ERROR_PROMPT = "目前还没有你的数据哟，请先联系管理员~"
NOT_EXIST_PROMPT = "目前OSS还没有存你的数据哟~"
DOWNLOAD_FAILED_PROMPT = "下载失败了，哭哭~"

ADDUSER_ARGS_PROMPT = "[学号，密码，邮箱]"

TWQDALL_SUCCESS_PROMPT = "签到完成啦！"
TWQDALL_RUNNING_PROMPT = "正在为您签到"
TWQDALL_NOT_IN_DATASET_PROMPT = "目前数据库没有你的数据哟"
TEQDALL_STUNUM_PROMPT = "你的学号是"

QUERY_ARGS_PROMPT = "学号 {}, 或 QQ {}"
QUERY_NO_DATA_PROMPT = "未查询到该用户"
QUERY_DATA_FORMAT = "学号:{}, QQ:{}"
QUERY_NO_SUCH_TYPE_PROMPT = "没有该类型数据"

SEND_LOG = False

ALKAID_POST_API = 'https://alkaid.cn1.utools.club/cpds/api/stu_twqd'
ADD_USER_API = 'https://alkaid.cn1.utools.club/cpdaily/api/item/quick_start'
