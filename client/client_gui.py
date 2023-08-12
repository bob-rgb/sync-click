import configparser
import queue
import socket
import threading
import time
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor


class ServerConnection:
    def __init__(self, addr):
        self.addr = addr
        self.client = None
        self.connected = False

    def connect(self):
        def _connect():
            try:
                self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client.connect(self.addr)
                print(f"成功连接到服务器: {self.addr}")
                self.connected = True
            except:
                print(f"服务器不在线: {self.addr}")
                self.connected = False

        with ThreadPoolExecutor() as executor:
            future = executor.submit(_connect)
            future.add_done_callback(self._handle_connect_result)

    def disconnect(self):
        self.client.close()
        self.connected = False

    def send(self, msg):
        if not self.connected:
            self.connect()

        with ThreadPoolExecutor() as executor:
            future = executor.submit(self._send, msg)
            future.add_done_callback(self._handle_send_result)

    def _send(self, msg):
        try:
            message = msg.encode(FORMAT)
            msg_length = len(message)
            send_length = str(msg_length).encode(FORMAT)
            send_length += b' ' * (HEADER - len(send_length))
            self.client.send(send_length)
            self.client.send(message)
            print(f'发送{msg}成功')
        except:
            self.connected = False

    def _handle_connect_result(self, future):
        if not future.cancelled():
            try:
                result = future.result()
            except:
                self.connected = False

    def _handle_send_result(self, future):
        if not future.cancelled():
            try:
                result = future.result()
            except:
                self.connected = False
                self.connect()


def send(msg):
    for server in servers:
        thread = threading.Thread(target=lambda s: s.send(msg), args=(server,))
        thread.start()


# 创建 ConfigParser 对象
config = configparser.ConfigParser()
config.read('config.ini')
servers_str = config.get('database', 'servers')
HEADER = 64
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

servers = []
for server_str in servers_str.split(','):
    host, port = server_str.split(':')
    servers.append(ServerConnection((host, int(port))))

status_update_queue = queue.Queue()
status_update_event = threading.Event()


def update_connection_status():
    for i, server in enumerate(servers):
        try:
            server.client.send(b'')
            server.connected = True
            status_update_queue.put((i, f"Server{i + 1} Connected", "green"))
        except:
            server.connected = False
            status_update_queue.put((i, f"Server{i + 1} Disconnected", "red"))
            server.connect()

    status_update_event.set()


def background_update_status():
    while True:
        status_update_event.wait()

        while not status_update_queue.empty():
            i, status, color = status_update_queue.get()
            connection_labels[i].config(text=status, fg=color)

        status_update_event.clear()

        time.sleep(5)
        update_connection_status()


def send_async(msg):
    thread = threading.Thread(target=send, args=(msg,))
    thread.start()


# call send_async from the GUI thread to send messages asynchronously
# def send_text(event=None):
#     text = text_entry.get()
#     send(text)
def toggle_always_on_top():
    root.attributes("-topmost", always_on_top_var.get())


# ------------
root = tk.Tk()
root.title("Client GUI")

button_frame = tk.Frame(root)
button_frame.pack(pady=20)

start_button = tk.Button(button_frame, text="开始采集", command=lambda: send_async("开始"), width=20, height=4)
start_button.grid(row=0, column=0, padx=10)

end_button = tk.Button(button_frame, text="结束采集", command=lambda: send_async("结束"), width=20, height=4)
end_button.grid(row=0, column=1, padx=10)

always_on_top_var = tk.BooleanVar()
always_on_top_checkbutton = tk.Checkbutton(root, text="Always on top", variable=always_on_top_var,
                                           command=toggle_always_on_top)
always_on_top_checkbutton.pack(pady=10)

connection_frame = tk.Frame(root)
connection_frame.pack(pady=10)

connection_labels = []
for i, server in enumerate(servers):
    label = tk.Label(connection_frame, text=f"Server {i + 1} - {'Connected' if server.connected else 'connecting...'}",
                     fg="green" if server.connected else "orange")
    label.pack()
    connection_labels.append(label)

# ----------------------------------
status_update_thread = threading.Thread(target=background_update_status)
status_update_thread.daemon = True
status_update_thread.start()

root.after(1000, update_connection_status)

root.mainloop()
