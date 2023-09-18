from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
import socket
import threading
import time

# 设置小车控制服务器的IP地址和端口
SERVER_IP = '192.168.137.216'
SERVER_PORT = 8080

# 创建TCP套接字
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 连接到小车控制服务器
client_socket.connect((SERVER_IP, SERVER_PORT))

# 发送指令到小车
def send_command(command):
    client_socket.send(command.encode())

# 更改服务器IP地址
def change_server_ip(ip_address):
    global SERVER_IP, client_socket
    client_socket.close()
    SERVER_IP = ip_address
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, SERVER_PORT))

# 定义应用程序界面
class CarControlLayout(GridLayout):

    # 初始化方法
    def __init__(self, **kwargs):
        # 调用父类的初始化方法
        super(CarControlLayout, self).__init__(**kwargs)

        # 设置列数为2
        self.cols = 2

        # 创建按钮并绑定相应的指令
        forward_btn = Button(text='Forward')
        forward_btn.bind(on_press=lambda x: self.queue_command('1'))
        self.add_widget(forward_btn)

        backward_btn = Button(text='Backward')
        backward_btn.bind(on_press=lambda x: self.queue_command('2'))
        self.add_widget(backward_btn)

        left_btn = Button(text='Left')
        left_btn.bind(on_press=lambda x: self.queue_command('3'))
        self.add_widget(left_btn)

        right_btn = Button(text='Right')
        right_btn.bind(on_press=lambda x: self.queue_command('4'))
        self.add_widget(right_btn)

        stop_btn = Button(text='Stop')
        stop_btn.bind(on_press=lambda x: self.queue_command('0'))
        self.add_widget(stop_btn)

        # 创建一个输入框和'Change IP'按钮
        self.ip_input = TextInput(text='Enter new IP here', multiline=False)
        self.add_widget(self.ip_input)
        change_ip_btn = Button(text='Change IP')
        change_ip_btn.bind(on_press=self.change_ip)
        self.add_widget(change_ip_btn)

        # 创建一个锁，用于控制指令的执行
        self.command_lock = threading.Lock()

        # 初始化指令队列和执行状态
        self.command_queue = []
        self.execute_commands = True

        # 启动一个线程来执行指令队列
        threading.Thread(target=self.process_commands).start()

    # 定义一个方法，将指令添加到指令队列中
    def queue_command(self, command):
        self.command_lock.acquire()
        self.command_queue.append(command)
        self.command_lock.release()

    # 定义一个方法，用于执行指令队列中的指令
    def process_commands(self):
        while self.execute_commands:
            if self.command_queue:
                self.command_lock.acquire()
                command = self.command_queue.pop(0)
                self.command_lock.release()
                send_command(command)
                time.sleep(0.1)

    # 定义一个方法，当'Change IP'按钮被按下时取回新的ip值并执行IP地址变更
    def change_ip(self, instance):
        new_ip = self.ip_input.text
        change_server_ip(new_ip)

    # 定义一个方法，用于停止执行指令队列
    def stop_execution(self):
        self.command_lock.acquire()
        self.command_queue.clear()
        self.execute_commands = False
        self.command_lock.release()

# 定义应用程序
class CarControlApp(App):

    # 定义一个方法，用来构建app的界面
    def build(self):
        # 返回一个CarControlLayout的实例
        return CarControlLayout()

    # 定义一个方法，在应用程序关闭时停止指令队列执行
    def on_stop(self):
        self.root.stop_execution()

# 启动应用程序
if __name__ == '__main__':
    app = CarControlApp()
    app.run()