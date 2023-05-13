import sys

from PyQt5.QtWidgets import QApplication
from client_2 import Client
from UIManager import MainWindow


def main():

    client1 = Client()
    client1.connect_to_server()
    client1.run()
    app = QApplication(sys.argv)
    window = MainWindow(client1)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
