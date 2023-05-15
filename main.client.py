import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication
from server import Server
from client import Client
import threading
from UIManager import MainWindow
import qdarkstyle


def main():

    client1 = Client()
    client1.connect_to_server()
    client1.run()
    app = QApplication(sys.argv)
    # app.setStyle(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    # Задаем темный стиль оформления
    # app.setStyle('Fusion')
    # palette = app.palette()
    # palette.setColor(palette.Window, Qt.darkCyan)
    # palette.setColor(palette.WindowText, Qt.white)
    # # palette.setColor(palette.Base, Qt.darkGray)
    # palette.setColor(palette.AlternateBase, Qt.gray)
    # palette.setColor(palette.ToolTipBase, Qt.white)
    # palette.setColor(palette.ToolTipText, Qt.white)
    # palette.setColor(palette.Text, Qt.darkGray)
    # palette.setColor(palette.Button, Qt.darkGray)
    # palette.setColor(palette.ButtonText, Qt.white)
    # palette.setColor(palette.BrightText, Qt.red)
    # app.setPalette(palette)

    # Задаем шрифт для всех виджетов
    # font = QFont('Arial', 10)
    # app.setFont(font)
    window = MainWindow(client1)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
