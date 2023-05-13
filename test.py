# import sys
# from PyQt5.QtCore import Qt
# from PyQt5.QtGui import QPalette, QColor
# from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit, QStyleFactory, QSizePolicy, QGridLayout, QSpacerItem
#
# class VideoPlayer(QWidget):
#     def __init__(self):
#         super().__init__()
#
#         # Создание видео плеера
#         self.video_player = QLabel('Видео будет здесь')
#         self.video_player.setAlignment(Qt.AlignCenter)
#
#         # Создание кнопок управления видео
#         self.play_button = QPushButton('Play')
#         self.pause_button = QPushButton('Pause')
#         self.stop_button = QPushButton('Stop')
#
#         # Создание чата и поля ввода сообщения
#         self.chat_history = QTextEdit()
#         self.chat_history.setReadOnly(True)
#
#         self.chat_input = QLineEdit()
#         self.chat_input.setPlaceholderText('Введите сообщение')
#         self.send_button = QPushButton('Отправить')
#
#         # Создание вертикального слоя для кнопок управления видео
#         control_button_layout = QVBoxLayout()
#         control_button_layout.addWidget(self.play_button)
#         control_button_layout.addWidget(self.pause_button)
#         control_button_layout.addWidget(self.stop_button)
#
#         # Создание горизонтального слоя для видео плеера и кнопок управления видео
#         video_control_layout = QHBoxLayout()
#         video_control_layout.addWidget(self.video_player)
#         video_control_layout.addLayout(control_button_layout)
#
#         # Создание вертикального слоя для чата
#         chat_layout = QVBoxLayout()
#         chat_layout.addWidget(self.chat_history)
#         chat_layout.addWidget(self.chat_input)
#         chat_layout.addWidget(self.send_button)
#
#         # Создание главного слоя
#         main_layout = QGridLayout()
#         main_layout.addLayout(video_control_layout, 0, 0, 2, 1)
#         main_layout.addLayout(chat_layout, 0, 1)
#         main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding), 1, 1)
#
#         # Установка главного слоя в качестве макета для виджета
#         self.setLayout(main_layout)
#
#         # Назначение обработчиков событий для кнопок
#         self.play_button.clicked.connect(self.play_video)
#         self.pause_button.clicked.connect(self.pause_video)
#         self.stop_button.clicked.connect(self.stop_video)
#         self.send_button.clicked.connect(self.send_message)
#
#     def play_video(self):
#         # Обработчик нажатия на кнопку "Play"
#         pass
#
#     def pause_video(self):
#         # Обработчик нажатия на кнопку "Pause"
#         pass
#
#     def stop_video(self):
#         # Обработчик нажатия на кнопку "Stop"
#         pass
#
#     def send_message(self):
#         # Обработчик нажатия на кнопку "Отправить"
#         pass
#
# if __name__ == '__main__':
#     # Создание приложения и виджета
#     app = QApplication(sys.argv)
#     video_player = VideoPlayer()
#     video_player.show()
#     sys.exit(app.exec_())



#
# if __name__ == '__main__':
#     app = QApplication([])
#     main_window = MainWindow()
#     # main_window.resize(1366, 768)
#     main_window.show()
#     app.exec_()

from PyQt5.QtWidgets import QWidget, QListWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QApplication
from PyQt5.QtCore import Qt, pyqtSignal



if __name__ == '__main__':
    app = QApplication([])
    main_window = ChatWidget()
    # main_window.resize(1366, 768)
    main_window.show()
    app.exec_()