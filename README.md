## Introduction

本项目基于<a href="https://github.com/nonebot/nonebot2">nonebot2</a>和<a href="https://github.com/Mrs4s/go-cqhttp">go-cqhttp</a>开发，用于HainanUnverisity的同学进行每日的体温上报，并可发送截图

后端使用MySQL存储QQ-学号映射，API由[`ALKAID`](https://github.com/QIN2DIM/CampusDailyAutoSign)提供

- ps: 对于HainanUnverisity的同学，可以将bot(851722457)拉到群中进行签到，bot会自动同意加群和好友请求. 如需twqdall，请联系superadmin(729320011,471591513)，进行信息录入

## 食用指北

### 部署和配置

```sh
pip install nb-cli
pip install -r requestments.txt
# cd到nonebot2插件目录
git clone git@github.com:beiyuouo/hnu-temp-report-bot.git
# 修改配置
# 查找字段 "# CHANGE" 修改成自己的配置即可
# 需要修改的内容
# alkaidapi.py
ALKAID_HOST = '' # CHANGE ALKAIDAPI HOST
QQMAP_HOST = '' # CHANGE 数据库HOST
QQMAP_USERNAME = '' # CHANGE 数据库用户名
QQMAP_PASSWORD = '' # CHANGE 数据库密码

# config.py
PLUGINS_PATH = 'awesome_bot/plugins/hnu-temp-report-bot' # CHANGE 插件目录
GOCQ_PATH = '' # CHANGE GO-CQHTTP运行目录

# alioss.py
AccessKeyId = '' # CHANGE OSS key
AccessKeySecret = '' # CHANGE OSS secret
bucket_name = '' # CHANGE OSS bucket
oss2.Bucket(auth, '', bucket_name) # CHANGE OSS host

# 建立MySQL数据库和表结构
# 内容在sql.sql文件中
# 启动bot
python bot.py
```

### 命令

- `@bot twqd 学号`: 调用ALKAID API进行体温签到（无需密码），如需要截图，则需要录入ALKAID数据库中
- `@bot twqdall`: 将群内所有人qq和学号映射，并进行签到，需要superadmin权限
- `@bot query [qq|学号] [{}]`: 查询MySQL中数据映射
- `@bot add [学号]`: 以@bot的用户QQ和学号进行映射，存入数据库中
- `@bot add [qq] [学号]`: 一对键值存入数据库中

## TODO

- [ ] 参数检查
- [ ] 超级用户管理
- [ ] QQ学号映射管理