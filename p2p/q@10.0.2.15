import socket
from pynat import get_ip_info

def get_ip_addr():

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    topology, ext_ip, ext_port = get_ip_info()
    s.connect((ext_ip, ext_port))
    return s.getsockname()[0]


if __name__ == "__main__":

    sock = socket.socket()
    try:
        print("IP: {}".format(get_ip_addr()))
        server_ip = input("Введите IP ")
        print("Подключение к серверу...")
        sock.connect((server_ip, 9090))
        print("Соединение установлено")
        
        while True:
            client_mess = input("Клиент: ")
            sock.send(client_mess.encode())
            if client_mess == "выход":
                break

            server_mess = sock.recv(1024).decode()
            print("Сервер: ", server_mess)
    except Exception as err:
        print('Ошибка ', err)
    finally:
        sock.close()
