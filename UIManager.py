import sys
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout
from client import Client

class VideoWindow(QMainWindow):
    def __init__(self, client: Client):
        super().__init__()
        self.setWindowTitle('Video Stream')
        self._client = client

        # Создание виджета для отображения видео
        self.video_widget = QLabel(self)
        self.video_widget.setAlignment(Qt.AlignCenter)

        # Создание кнопки для включения/выключения стриминга видео
        self.toggle_stream_button = QPushButton('Start Stream', self)
        self.toggle_stream_button.clicked.connect(self.toggle_stream)

        # Создание главного виджета и размещение виджетов на нем
        main_widget = QWidget(self)
        main_layout = QVBoxLayout(main_widget)
        main_layout.addWidget(self.video_widget)
        main_layout.addWidget(self.toggle_stream_button)

        # Установка главного виджета в качестве центрального виджета окна приложения
        self.setCentralWidget(main_widget)

        self._client.frame_received.connect(self.update_video_frame)

        # Создание экземпляра класса VideoStreamer для стриминга видео
        # self.streamer = VideoStreamer()

    def toggle_stream(self, frame):
        if self._client._is_screen_stream:
            self._client.send_command_ui(5)
            self.toggle_stream_button.setText('Start Stream')
        else:
            self._client.send_command_ui(5)
            self.toggle_stream_button.setText('Stop Stream')

    def update_video_frame(self, frame):
        # Конвертирование numpy-массива в изображение PyQt5
        q_image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_BGR888)
        q_pixmap = QPixmap.fromImage(q_image)

        # Обновление виджета для отображения видео
        self.video_widget.setPixmap(q_pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    video_window = VideoWindow()
    video_window.show()
    sys.exit(app.exec_())
