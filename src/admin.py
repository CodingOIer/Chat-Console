import requests

ip = input('服务器 ip 地址: ')
rootToken = input('Root 用户密钥: ')

if __name__ == '__main__':
    baseURL = ''
    if ip.find(':') == -1:
        baseURL = f'http://{ip}:47197'
    else:
        baseURL = f'http://{ip}'
    while True:
        op = input('$ ')
        if op == 'invite':
            response = requests.post(
                url=f'{baseURL}/root',
                json={
                    'token': rootToken,
                    'do': 'invite',
                },
            )
            print(response.text)
        elif op == 'ban ip':
            target = input('需要封禁的 ip: ')
            response = requests.post(
                url=f'{baseURL}/root',
                json={
                    'token': rootToken,
                    'do': 'ban ip',
                    'ip': target,
                },
            )
            print(response.text)
        elif op == 'allow ip':
            target = input('需要加入白名单的 ip: ')
            response = requests.post(
                url=f'{baseURL}/root',
                json={
                    'token': rootToken,
                    'do': 'allow ip',
                    'ip': target,
                },
            )
            print(response.text)
        elif op == 'block':
            key = input('需要删除的用户 Token：')
            response = requests.post(
                url=f'{baseURL}/root',
                json={
                    'token': rootToken,
                    'do': 'block',
                    'key': key,
                },
            )
        elif op == 'mute':
            key = input('需要禁言的用户 Token：')
            response = requests.post(
                url=f'{baseURL}/root',
                json={
                    'token': rootToken,
                    'do': 'mute',
                    'key': key,
                },
            )
        elif op == 'unmute':
            key = input('需要解除禁言的用户 Token：')
            response = requests.post(
                url=f'{baseURL}/root',
                json={
                    'token': rootToken,
                    'do': 'unmute',
                    'key': key,
                },
            )
