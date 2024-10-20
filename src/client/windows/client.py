import sys
import time
import threading
import requests
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit
from PyQt5.QtCore import pyqtSignal, QObject
import queue


class Communicate(QObject):
    message_received = pyqtSignal(str)  # 信号用于接收消息
    send_message = pyqtSignal(str)  # 信号用于发送消息


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.c = Communicate()
        self.c.message_received.connect(self.handle_message)
        self.c.send_message.connect(self.handle_send_message)

    def initUI(self):
        self.setWindowTitle('Chat-Console')

        self.layout = QVBoxLayout()

        # 多行文本显示区
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.layout.addWidget(self.text_edit)

        # 单行输入框
        self.line_edit = QLineEdit()
        self.line_edit.returnPressed.connect(self.on_return_pressed)
        self.layout.addWidget(self.line_edit)

        self.setLayout(self.layout)
        self.resize(400, 300)
        self.show()

    def printScreen(self, msg):
        """
        追加多行文本到文本显示区
        """
        self.text_edit.append(msg)

    def on_return_pressed(self):
        """
        当用户按下 Enter 键时，触发此方法
        """
        text = self.line_edit.text().strip()
        if text:
            self.line_edit.clear()
            self.c.send_message.emit(text)  # 发送消息信号

    def handle_message(self, msg):
        """
        处理接收到的消息
        """
        self.printScreen(msg)

    def handle_send_message(self, msg):
        """
        处理发送消息的信号
        """
        send_queue.put(msg)  # 将消息放入发送队列


# 全局消息队列
send_queue = queue.Queue()


def listen(ip, token, communicator):
    """
    监听服务器消息并通过信号传递给主线程
    """
    last = 0
    baseURL = f'http://{ip}' if ':' in ip else f'http://{ip}:47197'
    while True:
        try:
            response = requests.post(
                f'{baseURL}/', json={'token': token, 'do': 'messages'}
            )
            js = response.json()
            count = len(js)
            for i in range(last, count):
                x = js[i]
                if x.get('sendto') == '$PUBLIC':
                    message = (
                        f"[{x.get('username', 'Unknown')}]: {x.get('message', '')}"
                    )
                    communicator.message_received.emit(message)
                elif x['you']:
                    message = f"[Send PM to {x.get('sendto', 'Unknown')}]: {x.get('message', '')}"
                    communicator.message_received.emit(message)
                else:
                    message = f"[PM from {x.get('username', 'Unknown')}]: {x.get('message', '')}"
                    communicator.message_received.emit(message)
            last = count
        except Exception as e:
            communicator.message_received.emit(f"错误: {str(e)}")
        time.sleep(0.1)  # 调整轮询间隔时间


def rmb(s, w):
    index = s.find(w)
    if index != -1:
        return s[index + 1 :]
    return s


def send_messages(ip, token, window):
    """
    发送消息到服务器
    """
    baseURL = f'http://{ip}' if ':' in ip else f'http://{ip}:47197'
    while True:
        try:
            msg = send_queue.get()
            op = msg.split(' ')[0]
            if op == '/reg':
                response = requests.post(
                    f'{baseURL}/',
                    json={
                        'token': token,
                        'do': 'register',
                        'username': msg.split(' ')[1],
                    },
                )
                window.printScreen(response.text)
            elif op == '/msg':
                to = msg.split(' ')[1]
                msg = msg[len(msg.split(' ')[1]) + 6 : len(msg) : 1]
                response = requests.post(
                    f'{baseURL}/',
                    json={
                        'token': token,
                        'do': 'send',
                        'sendto': to,
                        'message': msg,
                    },
                )
                if response.status_code != 200:
                    window.printScreen(response.text)
            else:
                response = requests.post(
                    f'{baseURL}/',
                    json={
                        'token': token,
                        'do': 'send',
                        'sendto': '$PUBLIC',
                        'message': msg,
                    },
                )
                if response.status_code != 200:
                    window.printScreen(response.text)
        except:
            pass


def main():
    # 获取服务器 IP 地址和用户密钥
    ip = input('服务器 IP 地址: ').strip()
    token = input('用户密钥: ').strip()

    app = QApplication(sys.argv)
    window = MyWindow()

    # 显示欢迎信息
    """ window.printScreen("欢迎使用 PyQt5 窗口！")
    window.printScreen("请输入一些内容，然后按 Enter。") """

    # 启动监听线程
    listen_thread = threading.Thread(
        target=listen, args=(ip, token, window.c), daemon=True
    )
    listen_thread.start()

    # 启动发送线程
    send_thread = threading.Thread(
        target=send_messages, args=(ip, token, window), daemon=True
    )
    send_thread.start()

    # 启动 Qt 事件循环
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
