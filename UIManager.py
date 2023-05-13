import sys
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, \
    QStackedWidget, QMainWindow, QMessageBox, QComboBox, QListWidget

from client import Client


class VideoWidgetTwo(QWidget):
    def __init__(self, parent=None, client: Client = None):
        super().__init__(parent)
        self.setWindowTitle('Video Stream')
        self.client = client

        # Создание виджета для отображения видео
        self.video_widget = QLabel(self)
        self.video_widget.setAlignment(Qt.AlignCenter)

        # Создание кнопки для включения/выключения стриминга видео
        self.toggle_stream_button = QPushButton('Start Stream', self)
        self.toggle_stream_button.clicked.connect(self.toggle_stream)

        # Создание главного виджета и размещение виджетов на нем
        # main_widget = QWidget(self)
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.video_widget)
        main_layout.addWidget(self.toggle_stream_button)
        self.setLayout(main_layout)
        # self.client.frame_received.connect(self.update_video_frame)

    def toggle_stream(self):
        if self.client._is_screen_stream:
            self.client.send_screenshare()
            self.toggle_stream_button.setText('Start Stream')
        else:
            self.client.send_screenshare()
            self.toggle_stream_button.setText('Stop Stream')

    def update_video_frame(self, frame):
        # Конвертирование numpy-массива в изображение PyQt5
        q_image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_BGR888)
        q_pixmap = QPixmap.fromImage(q_image)
        # Обновление виджета для отображения видео
        self.video_widget.setPixmap(q_pixmap)


class LoginWidget(QWidget):
    def __init__(self, parent=None, client: Client = None):
        super().__init__(parent)
        self.client = client
        email_label = QLabel('Email')
        self.email_input = QLineEdit()

        password_label = QLabel('Password')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        login_button = QPushButton('Войти')
        register_button = QPushButton('Зарегистрироваться')

        login_button.clicked.connect(self.login)
        self.client.update_is_authorized.connect(self.is_logined)
        register_button.clicked.connect(self.show_register_widget)

        layout = QVBoxLayout()
        layout.addWidget(email_label)
        layout.addWidget(self.email_input)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(login_button)
        layout.addWidget(register_button)

        self.setLayout(layout)

    def login(self):
        self.client.send_login_user(self.email_input.text(), self.password_input.text())
        self.email_input.clear()
        self.password_input.clear()
        # GET STATUS LOGIN

    def is_logined(self, flag):
        if flag:
            self.parent().setCurrentIndex(2)
        else:
            QMessageBox.warning(self.parent(), 'Error', 'Cant login')

    def show_register_widget(self):
        self.email_input.clear()
        self.password_input.clear()
        self.parent().setCurrentIndex(1)


class RegisterWidget(QWidget):
    def __init__(self, parent=None, client: Client = None):
        super().__init__(parent)
        self.client = client
        email_label = QLabel('Email')
        self.email_input = QLineEdit()

        password_label = QLabel('Password')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        username_label = QLabel('Username')
        self.username_input = QLineEdit()

        confirm_button = QPushButton('Подтвердить')
        login_button = QPushButton('Войти')

        confirm_button.clicked.connect(self.signup)
        self.client.update_is_authorized.connect(self.is_logined)
        login_button.clicked.connect(self.show_login_widget)

        layout = QVBoxLayout()
        layout.addWidget(email_label)
        layout.addWidget(self.email_input)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(confirm_button)
        layout.addWidget(login_button)

        self.setLayout(layout)

    def is_logined(self, flag):
        if flag:
            self.parent().setCurrentIndex(2)
        else:
            QMessageBox.warning(self.parent(), 'Error', 'Current email is occupied. Try again')

    def show_login_widget(self):
        self.parent().setCurrentIndex(0)
        self.email_input.clear()
        self.password_input.clear()
        self.username_input.clear()

    def signup(self):
        self.client.send_create_user(self.email_input.text(), self.password_input.text(), self.username_input.text())
        self.email_input.clear()
        self.password_input.clear()
        self.username_input.clear()
        # GET STATUS LOGIN
        # self.parent().setCurrentIndex(2)


class UserInfoWidget(QWidget):
    def __init__(self, client: Client = None):
        super().__init__()
        self.client = client

        self.username_label = QLabel(f"Username: {self.client.username}")
        self.client.update_username.connect(self.update_username_label)
        self.email_label = QLabel(f"Email: {self.client.email}")
        self.client.update_email.connect(self.update_email_label)
        self.logout_button = QPushButton("Logout")
        self.logout_button.clicked.connect(self.logout)

        # создаем вертикальный layout и добавляем виджеты
        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.email_label)
        layout.addWidget(self.logout_button)

        self.setLayout(layout)

    def update_username_label(self, new_username):
        self.username_label.setText(f"Username: {new_username}")

    def update_email_label(self, new_email):
        self.email_label.setText(f"Email: {new_email}")

    def logout(self):
        # переход на stacked_widget с индексом 0
        self.client.send_logout_user()
        self.parent().parent().setCurrentIndex(0)
        # сброс информации о пользователе
        # self.client.username = ""
        # self.client.email = ""
        self.username_label.setText("Username: ")
        self.email_label.setText("Email: ")


class RoomWidget(QWidget):
    def __init__(self, client: Client = None):
        super().__init__()
        self.client = client

        self.create_room_label = QLabel("Create room:")
        self.create_room_edit = QLineEdit()
        self.create_room_button = QPushButton("Create")

        self.connect_room_label = QLabel("Connect to room:")
        self.connect_room_edit = QLineEdit()
        self.connect_room_button = QPushButton("Connect")

        self.join_room_label = QLabel("Available rooms:")
        self.join_room_combobox = QComboBox()
        self.client.update_room_list.connect(self.update_room_list)
        self.join_room_button = QPushButton("Join")

        # подключаем сигналы к обработчикам
        self.create_room_button.clicked.connect(self.create_room)
        self.join_room_button.clicked.connect(self.join_room)
        self.connect_room_button.clicked.connect(self.connect_room)
        self.client.update_active_room.connect(self.is_joined)
        # создаем вертикальный layout и добавляем виджеты
        layout = QVBoxLayout()
        layout.addWidget(self.create_room_label)
        layout.addWidget(self.create_room_edit)
        layout.addWidget(self.create_room_button)
        layout.addWidget(self.connect_room_label)
        layout.addWidget(self.connect_room_edit)
        layout.addWidget(self.connect_room_button)
        layout.addWidget(self.join_room_label)
        layout.addWidget(self.join_room_combobox)
        layout.addWidget(self.join_room_button)

        self.setLayout(layout)

    def create_room(self):
        # получаем имя комнаты из поля ввода
        room_name = self.create_room_edit.text()
        # отправляем запрос на создание комнаты
        # и обновляем список комнат в combobox
        self.client.send_create_room(room_name)
        # self.update_room_list()

    def connect_room(self):
        # получаем имя выбранной комнаты из combobox
        room_name = self.connect_room_edit.text()
        # отправляем запрос на вступление в комнату
        self.client.send_join_room(room_name)
        # IS TRUE?

    def is_joined(self, name):
            self.parent().parent().setCurrentIndex(3)
            self.create_room_edit.clear()
            self.connect_room_edit.clear()

    def join_room(self):
        # получаем имя выбранной комнаты из combobox
        room_name = self.join_room_combobox.currentText()
        # отправляем запрос на вступление в комнату
        self.client.send_join_room(room_name)
        # IS TRUE?
        # if is_joined:
        #     self.parent().parent().setCurrentIndex(3)

    def update_room_list(self, room_name_list):
        # очищаем список комнат и заполняем его заново
        self.join_room_combobox.clear()
        # self.client.send_get_room_list()
        self.join_room_combobox.addItems(room_name_list)

class ChatWidget(QWidget):
    # send_message = pyqtSignal(str)

    def __init__(self, client: Client = None):
        super().__init__()
        self.client = client
        # Создаем QListWidget для отображения сообщений
        self.messages_list = QListWidget(self)
        self.messages_list.setWordWrap(True)

        # Создаем QLineEdit и QPushButton для отправки сообщений
        self.message_lineedit = QLineEdit(self)
        self.send_button = QPushButton('Send', self)
        self.send_button.clicked.connect(self.on_send_button_clicked)
        self.client.update_message.connect(self.add_message)
        self.client.update_whole_chat.connect(self.update_whole_chat)

        # Создаем вертикальный лэйаут для размещения виджетов
        v_layout = QVBoxLayout()
        v_layout.addWidget(self.messages_list)

        # Создаем горизонтальный лэйаут для размещения виджетов ввода сообщений
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.message_lineedit)
        h_layout.addWidget(self.send_button)
        v_layout.addLayout(h_layout)

        # Устанавливаем главный лэйаут для виджета
        self.setLayout(v_layout)

    def update_whole_chat(self, messages):
        self.clear_messages()
        for message in messages:
            self.messages_list.addItem(f"[{message[1]}] {message[0]}: {message[2]}")

    def add_message(self, message):
        self.messages_list.addItem(f"[{message[1]}] {message[0]}: {message[2]}")

    def clear_messages(self):
        """
        Очищает QListWidget от сообщений
        """
        self.messages_list.clear()

    def on_send_button_clicked(self):
        """
        Обработчик нажатия на кнопку отправки сообщения
        """
        message = self.message_lineedit.text()
        if message:
            # self.send_message.emit(message)
            self.client.send_chat(message)
            self.message_lineedit.clear()


class UserListWidget(QWidget):
    def __init__(self, client: Client = None):
        super().__init__()
        self.client = client

        self.user_list = QListWidget()

        layout = QVBoxLayout()
        layout.addWidget(self.user_list)
        self.setLayout(layout)
        # вызываем метод для загрузки пользователей
        self.load_users()
        self.client.update_user_list.connect(self.load_users)

    def load_users(self):
        # получаем список пользователей
        users = self.client.get_users_in_room()
        # очищаем список
        self.user_list.clear()
        # добавляем пользователей в список
        for user in users:
            self.user_list.addItem(user.username)


class VideoWidget(QLabel):
    def __init__(self, client: Client, username, id):
        super().__init__()
        self.username = username
        self.client = client
        self.id = id
        self.setFixedSize(QSize(320, 240))  # Устанавливаем размер видео-окна
        self.setAlignment(Qt.AlignCenter)  # Центрируем видео в окне
        self.setScaledContents(True)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # Добавляем виджет с именем пользователя
        self.username_label = QLabel(self)
        self.username_label.setText(username)
        self.username_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.username_label)

        # Устанавливаем layout виджета
        self.setLayout(layout)

        self.client.update_video_frame.connect(self.update_frame)


    def update_frame(self, frame, id):
        if self.id == id:
            # Конвертирование numpy-массива в изображение PyQt5
            q_image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_BGR888)
            q_pixmap = QPixmap.fromImage(q_image)
            # Обновление виджета для отображения видео
            self.setPixmap(q_pixmap)

class ScreenWidget(QLabel):
    def __init__(self, client: Client, username, id):
        super().__init__()
        self.username = username
        self.client = client
        self.id = id
        self.setFixedSize(QSize(320, 240))  # Устанавливаем размер видео-окна
        self.setAlignment(Qt.AlignCenter)  # Центрируем видео в окне
        self.setScaledContents(True)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # Добавляем виджет с именем пользователя
        self.username_label = QLabel(self)
        self.username_label.setText(username)
        self.username_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.username_label)

        # Устанавливаем layout виджета
        self.setLayout(layout)
        self.client.update_screen_frame.connect(self.update_frame)


    def update_frame(self, frame, id):
        if self.id == id:
            # Конвертирование numpy-массива в изображение PyQt5
            q_image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_BGR888)
            q_pixmap = QPixmap.fromImage(q_image)
            # Обновление виджета для отображения видео
            self.setPixmap(q_pixmap)

class WrapperVideoWidget(QWidget):
    def __init__(self, client: Client):
        super().__init__()
        self.client = client
        self.current_video_index = 0
        self.video_widgets = []

        self.stacked_widget = QStackedWidget(self)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.stacked_widget)
        self.client.user_is_video_stream.connect(self.add_video_widget_controller)

        next_button_video = QPushButton("Следующее видео", self)
        next_button_video.clicked.connect(self.show_next_video)
        self.layout().addWidget(next_button_video)

        prev_button_video = QPushButton("Предыдущее видео", self)
        prev_button_video.clicked.connect(self.show_prev_video)
        self.layout().addWidget(prev_button_video)

    def add_video_widget_controller(self, flag, name, user_id):
        if flag:
            # Add video
            video_widget = VideoWidget(self.client, name, user_id)
            self.video_widgets.append(video_widget)
            self.stacked_widget.addWidget(video_widget)  # добавляем виджет на stacked widget
        else:
            # Remove video
            for video_widget in self.video_widgets:
                if video_widget.username == name:
                    self.video_widgets.remove(video_widget)
                    self.stacked_widget.removeWidget(video_widget)  # удаляем виджет со stacked widget



    def show_next_video(self):
        if self.video_widgets:
            if self.current_video_index is None:
                self.current_video_index = 0
            else:
                self.current_video_index = (self.current_video_index + 1) % len(self.video_widgets)
            self.stacked_widget.setCurrentIndex(self.current_video_index)

    def show_prev_video(self):
        if self.video_widgets:
            if self.current_video_index is None:
                self.current_video_index = 0
            else:
                self.current_video_index = (self.current_video_index - 1) % len(self.video_widgets)
            self.stacked_widget.setCurrentIndex(self.current_video_index)



    # def switch_video(self, index):
    #     if 0 <= index < len(self.video_widgets):
    #         # Скрытие предыдущего видео
    #         if self.current_video_index is not None:
    #             self.video_widgets[self.current_video_index].hide()
    #         # Отображение выбранного видео
    #         self.current_video_index = index
    #         self.video_widgets[self.current_video_index].show()



class WrapperScreenWidget(QWidget):
    def __init__(self, client: Client):
        super().__init__()
        self.client = client
        self.current_screen_index = 0
        self.screen_widgets = []

        self.stacked_widget = QStackedWidget(self)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.stacked_widget)
        self.client.user_is_screen_stream.connect(self.add_screen_widget_controller)

        next_button_screen = QPushButton("Следующее экран", self)
        next_button_screen.clicked.connect(self.show_next_screen)
        self.layout().addWidget(next_button_screen)

        prev_button_screen = QPushButton("Предыдущее экран", self)
        prev_button_screen.clicked.connect(self.show_prev_screen)
        self.layout().addWidget(prev_button_screen)

    def add_screen_widget_controller(self, flag, name, user_id):
        if flag:
            # Add video
            screen_widget = ScreenWidget(self.client, name, user_id)
            self.screen_widgets.append(screen_widget)
            self.stacked_widget.addWidget(screen_widget)  # добавляем виджет на stacked widget
        else:
            # Remove video
            for screen_widget in self.screen_widgets:
                if screen_widget.username == name:
                    self.screen_widgets.remove(screen_widget)
                    self.stacked_widget.removeWidget(screen_widget)  # удаляем виджет со stacked widget

    def show_next_screen(self):
        if self.screen_widgets:
            if self.current_screen_index is None:
                self.current_screen_index = 0
            else:
                self.current_screen_index = (self.current_screen_index + 1) % len(self.screen_widgets)
            self.stacked_widget.setCurrentIndex(self.current_screen_index)

    def show_prev_screen(self):
        if self.screen_widgets:
            if self.current_screen_index is None:
                self.current_screen_index = 0
            else:
                self.current_screen_index = (self.current_screen_index - 1) % len(self.screen_widgets)
            self.stacked_widget.setCurrentIndex(self.current_screen_index)

class ExitRoomWidget(QWidget):
    def __init__(self, client: Client):
        super().__init__()
        self.client = client
        exit_room_button = QPushButton("Покинуть комнату", self)
        exit_room_button.clicked.connect(self.exit_room)
        layout = QVBoxLayout()
        layout.addWidget(exit_room_button)
        self.setLayout(layout)

    def exit_room(self):
        self.client.send_leave_room()
        self.parent().parent().setCurrentIndex(2)

class ControlWidget(QWidget):
    def __init__(self, client: Client):
        super().__init__()
        self.client = client

        self.audio_button = QPushButton('Включить аудио', self)
        self.audio_button.setCheckable(True)
        self.audio_button.setChecked(False)
        self.audio_button.clicked.connect(self.audio_button_clicked)

        self.screen_button = QPushButton('Включить экран', self)
        self.screen_button.setCheckable(True)
        self.screen_button.setChecked(False)
        self.screen_button.clicked.connect(self.screen_button_clicked)

        self.video_button = QPushButton('Включить видео', self)
        self.video_button.setCheckable(True)
        self.video_button.setChecked(False)
        self.video_button.clicked.connect(self.video_button_clicked)

        layout = QVBoxLayout()
        layout.addWidget(QLabel('Управление функционалом'))
        layout.addWidget(self.audio_button)
        layout.addWidget(self.screen_button)
        layout.addWidget(self.video_button)
        self.setLayout(layout)

    def audio_button_clicked(self, checked):
        if checked:
            # Включить аудио
            # self.client.toggle_audio_stream.emit(True)
            self.client.send_audio()
        else:
            # Выключить аудио
            # self.client.toggle_audio_stream.emit(False)
            self.client.send_audio()

    def screen_button_clicked(self, checked):
        if checked:
            # Включить экран
            # self.client.toggle_screen_stream.emit(True)
            self.client.send_screenshare()
        else:
            # Выключить экран
            # self.client.toggle_screen_stream.emit(False)
            self.client.send_screenshare()

    def video_button_clicked(self, checked):
        if checked:
            # Включить видео
            # self.client.toggle_video_stream.emit(True)
            self.client.send_video()
        else:
            # Выключить видео
            # self.client.toggle_video_stream.emit(False)
            self.client.send_video()

class MainRoomPageWidget(QWidget):
    def __init__(self, parent=None, client: Client = None):
        super().__init__(parent)
        self.client = client

        user_list_widget = UserListWidget(client)
        chat_widget = ChatWidget(client)
        video_widget = WrapperVideoWidget(client)
        screen_widget = WrapperScreenWidget(client)
        control_widget = ControlWidget(client)
        exit_room_widget = ExitRoomWidget(client)

        layout = QVBoxLayout()
        layout.addWidget(user_list_widget)
        layout.addWidget(chat_widget)

        video_screen_layout = QHBoxLayout()
        video_screen_layout.addWidget(video_widget)
        video_screen_layout.addWidget(screen_widget)
        layout.addLayout(video_screen_layout)

        layout.addWidget(control_widget)
        layout.addWidget(exit_room_widget)
        self.setLayout(layout)


class MainUserPageWidget(QWidget):
    def __init__(self, parent=None, client: Client = None):
        super().__init__(parent)
        self.client = client
        user_info_widget = UserInfoWidget(client)
        room_widget = RoomWidget(client)

        layout = QVBoxLayout()
        layout.addWidget(user_info_widget)
        layout.addWidget(room_widget)
        self.setLayout(layout)

class MainWindow(QWidget):
    def __init__(self, client: Client):
        super().__init__()
        self.client = client
        self.stacked_widget = QStackedWidget()

        login_widget = LoginWidget(self.stacked_widget, self.client)
        register_widget = RegisterWidget(self.stacked_widget, self.client)
        main_room_page_widget = MainRoomPageWidget(self.stacked_widget, self.client)
        main_user_page_widget = MainUserPageWidget(self.stacked_widget, self.client)


        self.stacked_widget.addWidget(login_widget)
        self.stacked_widget.addWidget(register_widget)
        self.stacked_widget.addWidget(main_user_page_widget)
        self.stacked_widget.addWidget(main_room_page_widget)

        layout = QHBoxLayout()
        layout.addWidget(self.stacked_widget)

        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    video_window = VideoWidget()
    video_window.show()
    sys.exit(app.exec_())
