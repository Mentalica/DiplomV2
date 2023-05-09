import sys

from PyQt5.QtWidgets import QApplication

from UIManager import VideoWindow
from networkManager import NetworkManager
from server import Server
from client import Client
import threading


def main():
    client1 = Client()
    client1.connect_to_server()
    client1.run()


if __name__ == '__main__':
    main()
