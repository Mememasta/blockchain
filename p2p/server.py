import socket
from pynat import get_ip_info


def get_ip_addr():
    
    topology, ext_ip, ext_port = get_ip_info()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((ext_ip, ext_port))
    return s.getsockname()[0]

if __name__ == "__main__":

    topology, ext_ip, ext_port = get_ip_info()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    print("IP:{}. Жду подключения...".format(get_ip_addr()))
    sock.bind(("192.168.0.6", 54320))


    try:
        print("Соединение установленно:")

        while True:
            client_mess = sock.recvfrom(1024).decode()
            if not client_mess:
                break

            print("Клиент: ", client_mess)
            if client_mess == "выход":
                break

            sock.sendto(input("Сервер: ").encode(), ("46.147.132.65", 46222))
        print("Соединение закрыто")
    except Exception as err:
        print("Ошибка ", err)
    finally:
        sock.close()
