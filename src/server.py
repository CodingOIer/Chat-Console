import flask
import secrets
import string
import threading
import json
import logging
from loguru import logger as log

admin_token = ''

api = flask.Flask('API')


who = dict()
keys = dict()
mute = dict()
black = dict()
online = dict()
whatKey = dict()
nameUse = dict()
registerIP = dict()

whileList = False

message = list()


def getToken(length=64):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


@api.route('/root', methods=['POST'])
def adminConsole():
    if (
        black.get(flask.request.remote_addr, whileList)
        and flask.request.remote_addr != '127.0.0.1'
    ):
        log.warning(f'来自封禁 ip {flask.request.remote_addr} 的登陆尝试')
        return flask.Response(f'你的 ip 地址已被封禁', 401)
    js = json.loads(flask.request.data)
    if js['token'] != admin_token:
        log.warning(f'来自 {flask.request.remote_addr} 的错误的管理员密钥')
        return flask.Response('无权限', 401)
    if js['do'] == 'ban ip':
        black[js['ip']] = True
        log.success(
            f'成功添加 {js['ip']} 到黑名单，操作 ip： {flask.request.remote_addr}'
        )
        return flask.Response(f'成功添加 {js['ip']} 到黑名单', 200)
    elif js['do'] == 'allow ip':
        black[js['ip']] = False
        log.success(
            f'成功添加 {js['ip']} 到白名单，操作 ip： {flask.request.remote_addr}'
        )
        return flask.Response(f'成功添加 {js['ip']} 到白名单', 200)
    elif js['do'] == 'invite':
        newKey = getToken()
        keys[newKey] = True
        log.success(
            f'成功添加用户密钥： {newKey} ，操作 ip： {flask.request.remote_addr}'
        )
        return flask.Response(f'成功添加用户密钥： {newKey}', 200)
    elif js['do'] == 'block':
        keys[js['key']] = False
        log.success(
            f'成功删除用户密钥： {js['key']} ，操作 ip： {flask.request.remote_addr}'
        )
        try:
            registerIP.pop(who[js['key']])
            whatKey.pop(who[js['key']])
            who.pop(js['key'])
        except:
            pass
        return flask.Response(f'成功删除用户密钥：{ js['key']}', 200)
    elif js['do'] == 'mute':
        mute[js['key']] = True
        log.success(f'成功禁言用户 {js['key']} ，操作 ip： {flask.request.remote_addr}')
        return flask.Response(f'成功禁言用户 {js['key']}')
    elif js['do'] == 'unmute':
        mute[js['key']] = False
        log.success(
            f'成功解除禁言用户 {js['key']} ，操作 ip： {flask.request.remote_addr}'
        )
        return flask.Response(f'成功解除禁言用户 {js['key']}')
    else:
        log.warning(f'未知命令，操作 ip： {flask.request.remote_addr}')
        return flask.Response(f'未知命令', 404)


@api.route('/', methods=['POST'])
def mainAPIConsole():
    if (
        black.get(flask.request.remote_addr, whileList)
        and flask.request.remote_addr != '127.0.0.1'
    ):
        log.warning(f'来自封禁 ip {flask.request.remote_addr} 的登陆尝试')
        return flask.Response(f'你的 ip 地址已被封禁', 404)
    js = json.loads(flask.request.data)
    if not keys.get(js['token'], False):
        log.warning(f'无法校验的 Token，来自 {flask.request.remote_addr}')
        return flask.Response('无法校验的 Token，请重试', 401)
    if js['do'] == 'register':
        if who.get(js['token'], None) != None:
            log.info(f'{js['token']} 想要再次注册')
            return flask.Response('你已经注册', 400)
        else:
            if js['username'].find('$') != -1:
                log.warning(f'来自 {js['token']} 的不合法用户名')
                return flask.Response('用户名不合法', 401)
            elif nameUse.get(js['username'], False):
                log.warning(f'用户 Token {js['token']} 重复注册为 {js['username']}')
                return flask.Response('用户名已存在', 400)
            who[js['token']] = js['username']
            whatKey[js['username']] = js['token']
            nameUse[js['username']] = True
            log.success(f'{js['token']} 注册为了 {js['username']}')
            registerIP[js['token']] = flask.request.remote_addr
            return flask.Response(f'成功注册为 {js['username']}', 200)
    elif js['do'] == 'send':
        if who.get(js['token'], None) == None:
            log.warning(f'来自 {js['token']} 未注册但是希望发送消息')
            return flask.Response('你尚未注册', 400)
        if mute.get(js['token'], False):
            log.warning(f'用户 {js['token']} 已被禁言，但是仍然请求发送私信')
            return flask.Response('你已被禁言', 400)
        message.append(
            {
                'username': js['username'],
                'ip': flask.request.remote_addr,
                'sendto': js['sendto'],
                'message': js['message'],
            }
        )
        log.success(
            f'来自 Token {js['token']} ，ip： {flask.request.remote_addr} 给 {js['sendto']} 的新消息'
        )
        return flask.Response(f'发送成功', 200)
    elif js['do'] == 'who':
        if whatKey.get(js['username'], None) == None:
            log.info(f'无法找到用户： {js['username']}')
            return flask.Response(f'无法找到用户： {js['username']}', 400)
        else:
            key = whatKey[js['username']]
            data = {
                'username': js['username'],
                'registerIP': registerIP[key],
                'token': key[::-1][0:8:1],
            }
            log.success(f'来自 {js['token']} 查询的 {js['username']} 用户信息')
            return flask.Response(json.dumps(data), 200)
    elif js['do'] == 'messages':
        username = keys[js['token']]
        res = list()
        for x in message:
            if (
                x['username'] == username
                or x['sendto'] == username
                or x['sendto'] == '$PUBLIC'
            ):
                res.append(
                    {
                        'username': x['username'],
                        'sendto': x['sendto'],
                        'message': x['message'],
                    }
                )
        log.success(f'来自 {js['token']} 的历史消息请求，一共 {len(res)} 条')
        return flask.Response(json.dumps(res), 200)


if __name__ == '__main__':
    admin_token = getToken()
    log.success(admin_token)
    logging.getLogger('werkzeug').disabled = True
    threading.Thread(target=api.run('0.0.0.0', 47197)).start()
