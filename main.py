from server import Server
from client import Client
import threading


def main():
    server = Server()
    server.start()
    server.accept_connection()


if __name__ == '__main__':
    main()
