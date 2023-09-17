import random
import socket
import select

import threading
import time
from AndTools import pack_u, pack_b

from AndroidQQ.package.sso_server import get_sso_list

clients = []

client_info = {}
ip_address = ''
ip_list = {}


def repackage(data, client):
    """重组包体"""
    global client_info
    client_info[client]['data'] = client_info[client]['data'] + data

    pack_ = pack_u(client_info[client]['data'])

    while True:
        if pack_.get_len() <= 4:
            """小于4个字节直接跳出"""
            break
        _len = pack_.get_int()

        if _len <= pack_.get_len() + 4:
            _bin = pack_.get_bin(_len - 4)
            _func = client_info[client]['func']
            _func(_bin)
            client_info[client]['data'] = pack_.get_all()
            pack_ = pack_u(client_info[client]['data'])
        else:
            pack = pack_b()
            pack.add_int(_len)
            pack.add_bin(pack_.get_all())
            pack_ = pack_u(pack.get_bytes())
            break


def disconnect_client(client, clients, client_info):
    """断开客户端连接"""
    clients.remove(client)
    client.close()
    client_info.pop(client)


def receive_data_all():
    """接收全部连接的数据"""
    global client_info

    while True:
        time.sleep(0.1)
        # todo 下面代码存在问题
        if len(clients) == 0:
            continue
        # 从元组列表中提取客户端套接字
        readable, _, _ = select.select(clients, [], [], 0)  # timeout =0
        for client in readable:
            try:
                data = client.recv(1024)
            except ConnectionResetError:
                print("连接已被客户端重置。")
                disconnect_client(client, clients, client_info)
                continue
            if not data:
                disconnect_client(client, clients, client_info)
                print('断开连接')
            else:
                # print(f"从客户端收到的数据: {data.hex()}")
                repackage(data, client)


# def receive_data(sock):
#     while True:
#         data = sock.recv(1024)
#         if not data:
#             break
#         print(f"从服务器收到的数据: {data.hex()}")


def start_client(host=None, port=None, _func=None):
    if not host:
        if ip_list:
            random_item = random.choice(ip_list)
            host = random_item['1']
            port = random_item['2']
        else:
            # 没初始化ip列表前用这个快速连接
            host = '36.155.245.16'
            port = 8080

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    client_info[client] = {
        'data': b'',
        'func': _func
    }
    clients.append(client)
    return client


def get_ip_list():
    time.sleep(1)  # 超过一秒再去请求,防止测试时请求
    global ip_list
    ip_list = get_sso_list()


def start_tcp_service():
    """启动TCP服务"""
    receive_thread = threading.Thread(target=receive_data_all, daemon=True).start()
    threading.Thread(target=get_ip_list, daemon=True).start()
    print('启动接收线程')


start_tcp_service()

if __name__ == "__main__":
    pass
