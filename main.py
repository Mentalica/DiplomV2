from networkManager import NetworkManager
from server import Server
from client import Client
import threading


def main():
    server = Server()
    server.start()
    thread = threading.Thread(target=server.accept_connection)
    thread.start()
    client1 = Client()
    client1.connect_to_server()
    client2 = Client()
    client2.connect_to_server()
    client3 = Client()
    client3.connect_to_server()


if __name__ == '__main__':
    main()
