import socket
import threading
import concurrent.futures
import screenClick.screenClick as sc
import configparser

# 创建 ConfigParser 对象
config = configparser.ConfigParser()
config.read('config.ini')

# 获取配置项的值
SERVER = config.get('database', 'server')
PORT = config.getint('database', 'port')
CLICK_MODE = config.getint('database','click_mode')
X_POSITION1 = config.getint('database','x_position1')
Y_POSITION1 = config.getint('database','y_position1')
X_POSITION2 = config.getint('database','x_position2')
Y_POSITION2 = config.getint('database','y_position2')


# PORT = 50504
# SERVER = socket.gethostbyname(socket.gethostname())
HEADER = 64
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
STOP_SERVER_MESSAGE = "关闭服务器"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False
            elif msg == '开始':
                print("开始播放")
                if CLICK_MODE == 1:
                    sc.click_position(X_POSITION1,Y_POSITION1)
                else:
                    thread = threading.Thread(sc.start_play())
                    thread.start()
            elif msg == '结束':
                print("结束播放")
                if CLICK_MODE == 1:
                    sc.click_position(X_POSITION2,Y_POSITION2)
                else:
                    thread = threading.Thread(sc.finish_play())
                    thread.start()
            elif msg == STOP_SERVER_MESSAGE:
                connected = False
                print("收到关闭服务器指令，停止监听")

            print(f"[{addr}] {msg}")

    print(f"[NEW CONNECTION] {addr} disconnected.")
    conn.close()

def start():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        server.listen()
        print(f"[LISTENING] Server is listening on {SERVER}")
        while True:
            conn, addr = server.accept()
            executor.submit(handle_client, conn, addr)
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    print("STARTING server is starting...")
    start()