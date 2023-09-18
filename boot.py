import network
import socket
import machine

# Wi-Fi连接配置
WIFI_SSID = 'XWBSZOOM'
WIFI_PASSWORD = '12345678'

# 小车控制引脚配置
# 控制1个电机
p13 = machine.Pin(13, machine.Pin.OUT)
p12 = machine.Pin(12, machine.Pin.OUT)
# 控制1个电机
p14 = machine.Pin(14, machine.Pin.OUT)
p27 = machine.Pin(27, machine.Pin.OUT)

# 连接Wi-Fi
def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            pass
    print('WiFi connected')
    print('Network config:', wlan.ifconfig())

# 小车向前运动
def move_forward():
    p13.value(0)
    p12.value(1)
    p14.value(1)
    p27.value(0)

# 小车向后运动
def move_backward():
    p13.value(1)
    p12.value(0)
    p14.value(0)
    p27.value(1)

# 小车向左运动
def move_left():
    p13.value(1)
    p12.value(0)
    p14.value(1)
    p27.value(0)

# 小车向右运动
def move_right():
    p13.value(0)
    p12.value(1)
    p14.value(0)
    p27.value(1)

# 停止小车运动
def stop():
    p13.value(0)
    p12.value(0)
    p14.value(0)
    p27.value(0)

# 连接到Wi-Fi网络
connect_to_wifi()

# 创建TCP套接字
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 绑定本地信息
server_socket.bind(("", 8080))

# 设置为被动模式，监听客户端的连接请求
server_socket.listen(1)
print("Waiting for client connection...")

# 接收客户端连接
client_socket, client_address = server_socket.accept()
print("Client connected:", client_address)

# 初始化小车运行状态
current_command = 'stop'

# 无限循环，接收指令并控制小车移动
while True:
    # 接收指令数据
    data = client_socket.recv(1024)
    if not data:
        break

    # 解析指令
    command = data.decode().strip()

    # 根据指令改变小车运行状态
    if command == '1':  # 前进
        current_command = 'forward'
    elif command == '2':  # 后退
        current_command = 'backward'
    elif command == '3':  # 左转
        current_command = 'left'
    elif command == '4':  # 右转
        current_command = 'right'
    elif command == '0':  # 停止
        current_command = 'stop'
    else:  # 无效指令
        print("Invalid command:", command)

    # 根据当前指令控制小车运动
    if current_command == 'forward':
        move_forward()
    elif current_command == 'backward':
        move_backward()
    elif current_command == 'left':
        move_left()
    elif current_command == 'right':
        move_right()
    elif current_command == 'stop':
        stop()

# 关闭套接字
client_socket.close()
server_socket.close()
