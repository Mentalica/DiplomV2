from networkManager import NetworkManager
from server import Server
from client import Client
import threading


def main():
    client1 = Client()
    client1.connect_to_server()
    print("DONE")
    client1.run()


if __name__ == '__main__':
    main()
