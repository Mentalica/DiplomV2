import sys

from PyQt5.QtWidgets import QApplication
from server import Server
from client import Client
import threading
from UIManager import VideoWindow


def main():

    client1 = Client()
    client1.connect_to_server()
    client1.run()
    # app = QApplication(sys.argv)
    # video_window = VideoWindow(client1)
    # video_window.show()
    # sys.exit(app.exec_())


if __name__ == '__main__':
    main()
