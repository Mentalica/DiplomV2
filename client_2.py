import base64
import socket
import time
import threading
import zlib
from typing import List

import cv2
import numpy as np
import mss

import pyaudio
from consts import *
from chatMessage import ChatMessage
from user import User
from message_2 import Message
from messageType import MessageType
from audioRecorder import AudioRecorder

from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QWidget


class Client(QObject):
    toggle_stream = pyqtSignal(bool)
    frame_received = pyqtSignal(np.ndarray)
    update_video_frame = pyqtSignal(np.ndarray, int)
    update_screen_frame = pyqtSignal(np.ndarray, int)

    update_room_list = pyqtSignal(list)
    update_username = pyqtSignal(str)
    update_email = pyqtSignal(str)
    update_user_list = pyqtSignal(list)
    update_is_authorized = pyqtSignal(bool)
    update_active_room = pyqtSignal(str)
    update_user_id = pyqtSignal(int)
    update_whole_chat = pyqtSignal(list)
    update_message = pyqtSignal(list)
    flag_is_voice_stream = pyqtSignal(bool)
    flag_is_video_stream = pyqtSignal(bool)
    flag_is_screen_stream = pyqtSignal(bool)
    user_is_voice_stream = pyqtSignal(bool, str)
    user_is_video_stream = pyqtSignal(bool, str, int)
    user_is_screen_stream = pyqtSignal(bool, str, int)


    def __init__(self, parent=None):
        super().__init__()
        self._udp_id_to_send = None
        self._main_tcp_client_socket = None
        # client sockets
        self._cmd_tcp_client_socket = None
        self._screen_udp_client_socket = None
        self._voice_udp_client_socket = None
        self._video_udp_client_socket = None

        # server ports
        self._cmd_tcp_server_port = None
        self._screen_udp_server_port = None
        self._voice_udp_server_port = None
        self._video_udp_server_port = None

        # stream flags
        self._is_audio_stream = False
        self._is_video_stream = False
        self._is_screen_stream = False
        self._show_other_screen_stream = True
        self._show_other_video_stream = True
        self._show_other_audio_stream = True

        self._audio = AudioRecorder()
        self._room_name_list = []
        self._active_room = None
        self._users_in_room: List[User] = []
        self._is_authorized = False

        self._user_id = None
        self._username = None
        self._email = None
        self._password = None

        self._chat: List[ChatMessage] = []

        self.lock = threading.Lock()

        # self._audio_in = self._audio.in_stream_audio()
        # self._audio_out = self._audio.out_stream_audio()

    def connect_to_server(self):
        self._main_tcp_client_socket = self.connect_to_tcp_server(MAIN_TCP_SERVER_PORT)

        msg_type, msg_data = Message.receive_message_tcp(self._main_tcp_client_socket)
        print(f"[inf] {CLIENT}: msg data: {msg_data}\nmsg type: {msg_type}\nsocket: {self._main_tcp_client_socket}")
        ports = msg_data.decode().split("|")
        print(f"[RECEIVED] {CLIENT}: ports - {ports}")
        if msg_type == MessageType.ECHO:
            self._cmd_tcp_server_port = int(ports[0])
            self._udp_id_to_send = int(ports[0])
            self._cmd_tcp_client_socket = self.connect_to_tcp_server(self._cmd_tcp_server_port)
            self._screen_udp_server_port = int(ports[1])
            self._screen_udp_client_socket = self.connect_to_udp_server(self._screen_udp_server_port)
            self._voice_udp_server_port = int(ports[2])
            self._voice_udp_client_socket = self.connect_to_udp_server(self._voice_udp_server_port)
            self._video_udp_server_port = int(ports[3])
            self._video_udp_client_socket = self.connect_to_udp_server(self._video_udp_server_port)

        # self.connect_to_udp_server()

    def connect_to_udp_server(self, udp_server_port):
        udp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        Message.send_message_udp(udp_client_socket, MessageType.ECHO, b"OK", MAIN_SERVER_ADDRESS_CL, udp_server_port)
        msg = Message.receive_message_udp(udp_client_socket)
        if int(msg[0]) == MessageType.ECHO and msg[1].decode() == "OK":
            print(f"[OK] {CLIENT} Client connected to UDP server\n\tSocket: {udp_client_socket}")
        else:
            print(f"[ERROR] {CLIENT}: {msg}")
        return udp_client_socket

    def connect_to_tcp_server(self, tcp_port):
        tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to the server
        server_address = (MAIN_SERVER_ADDRESS_CL, tcp_port)
        # self._tcp_server_socket.connect((SERVER_ADDRESS, TCP_SERVER_PORT))
        tcp_client_socket.connect(server_address)  # FOR DIFF PCs
        print(f"[OK] {CLIENT} Client connected to TCP server\n\tSocket: {tcp_client_socket}")
        return tcp_client_socket

    def disconnect_from_server(self):
        self.close_udp_client_connection()
        self.close_tcp_client_connection()

    def close_udp_client_connection(self):
        # self._udp_client_socket.close()
        print(f"[OK] {CLIENT} UDP client disconnected")

    def close_tcp_client_connection(self):
        # self._tcp_client_socket.close()
        print(f"[OK] {CLIENT} TCP client disconnected")

    def run(self):
        threading.Thread(target=self.send_command).start()
        threading.Thread(target=self.handle_message).start()
        # self.send_message()
        # self.handle_message()

    def send_command(self):
        while True:
            time.sleep(0.1)  # STILL I HAVENT GUI
            if self._is_authorized:
                cmd = input(f"[ACTION-INPUT] {CLIENT} ({self._username}:{self._active_room}) Command number - ")
            else:
                cmd = input(f"[ACTION-INPUT] {CLIENT}(U re not authorized) ({self._active_room}) Command number - ")

            if int(cmd) == MessageType.ECHO:
                threading.Thread(target=Message.send_message_tcp,
                                 args=(self._cmd_tcp_client_socket, MessageType.ECHO, cmd.encode('utf-8'),)).start()

            elif int(cmd) == MessageType.AUDIO:
                threading.Thread(target=self.handle_audio_cmd).start()

            elif int(cmd) == MessageType.VIDEO:
                threading.Thread(target=self.handle_video_cmd).start()

            elif int(cmd) == MessageType.SCREENSHARE:
                threading.Thread(target=self.handle_screen_cmd).start()

            elif int(cmd) == MessageType.CREATE_ROOM:
                room_name = input(f"[INPUT] {CLIENT}: Room name to create - ")
                Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.CREATE_ROOM,
                                         room_name.encode('utf-8'))

            elif int(cmd) == MessageType.DELETE_ROOM:
                room_name = input(f"[INPUT] {CLIENT}: Room name to delete - ")
                Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.DELETE_ROOM,
                                         room_name.encode('utf-8'))

            elif int(cmd) == MessageType.JOIN_ROOM:
                room_name = input(f"[INPUT] {CLIENT}: Room name to join - ")
                Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.JOIN_ROOM, room_name.encode('utf-8'))

            elif int(cmd) == MessageType.LEAVE_ROOM:
                self._active_room = None
                Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.LEAVE_ROOM, OK_FLAG)

            elif int(cmd) == MessageType.GET_ROOM_LIST:
                Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.GET_ROOM_LIST, OK_FLAG)

            elif int(cmd) == MessageType.GET_CLIENT_LIST:
                Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.GET_CLIENT_LIST, OK_FLAG)

            elif int(cmd) == MessageType.LOGIN_USER:
                # ДОБАВИТЬ ПРОВЕРКУ НА АТОРИЗОВАННОСТЬ
                email = input(f"[LOGIN] {CLIENT}: Email - ")
                password = input(f"[LOGIN] {CLIENT}: Password - ")
                msg = "|".join([email, password])
                Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.LOGIN_USER, msg.encode())

            elif int(cmd) == MessageType.CREATE_USER:
                # ДОБАВИТЬ ПРОВЕРКУ НА АТОРИЗОВАННОСТЬ
                email = input(f"[SIGNUP] {CLIENT}: Email - ")
                password = input(f"[SIGNUP] {CLIENT}: Password - ")
                username = input(f"[SIGNUP] {CLIENT}: Username - ")
                msg = "|".join([email, password, username])

                Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.CREATE_USER, msg.encode())
            elif int(cmd) == MessageType.LOGOUT_USER:
                Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.LOGOUT_USER, OK_FLAG)

            elif int(cmd) == MessageType.CHAT:
                msg = input(f"[CHAT] {CLIENT}: Send message - ")
                Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.CHAT, msg.encode())

            elif int(cmd) == MessageType.UPDATE_CHAT:
                Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.UPDATE_CHAT, START_FLAG)
            # msg = input("[ACTION]: MSG - ")
            # Message.send_message_tcp(self._tcp_client_socket, MessageType.ECHO, cmd.encode('utf-8'))

    def send_command_ui(self, cmd):
        # while True:
        #     time.sleep(0.1)  # STILL I HAVENT GUI
        #     cmd = input(f"[ACTION-INPUT] {CLIENT}: Command number - ")
        # if int(cmd) == MessageType.ECHO:
        #     threading.Thread(target=Message.send_message_tcp,
        #                      args=(self._cmd_tcp_client_socket, MessageType.ECHO, cmd.encode('utf-8'),)).start()
        # elif int(cmd) == MessageType.AUDIO:
        #     threading.Thread(target=self.handle_audio_cmd).start()
        # elif int(cmd) == MessageType.VIDEO:
        #     threading.Thread(target=self.handle_video_cmd).start()
        # elif int(cmd) == MessageType.SCREENSHARE:
        #     threading.Thread(target=self.handle_screen_cmd).start()
        while True:
            time.sleep(0.1)  # STILL I HAVENT GUI

            if int(cmd) == MessageType.ECHO:
                self.send_echo()
            elif int(cmd) == MessageType.AUDIO:
                self.send_audio()
            elif int(cmd) == MessageType.VIDEO:
                self.send_video()
            elif int(cmd) == MessageType.SCREENSHARE:
                self.send_screenshare()
            elif int(cmd) == MessageType.CREATE_ROOM:
                pass
            elif int(cmd) == MessageType.DELETE_ROOM:
                room_name = input(f"[INPUT] {CLIENT}: Room name to delete - ")
                Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.DELETE_ROOM,
                                         room_name.encode('utf-8'))

            elif int(cmd) == MessageType.JOIN_ROOM:
                room_name = input(f"[INPUT] {CLIENT}: Room name to join - ")
                Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.JOIN_ROOM, room_name.encode('utf-8'))

            elif int(cmd) == MessageType.LEAVE_ROOM:
                self._active_room = None
                Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.LEAVE_ROOM, OK_FLAG)

            elif int(cmd) == MessageType.GET_ROOM_LIST:
                Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.GET_ROOM_LIST, OK_FLAG)

            elif int(cmd) == MessageType.GET_CLIENT_LIST:
                Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.GET_CLIENT_LIST, OK_FLAG)

            elif int(cmd) == MessageType.LOGIN_USER:
                # ДОБАВИТЬ ПРОВЕРКУ НА АТОРИЗОВАННОСТЬ
                email = input(f"[LOGIN] {CLIENT}: Email - ")
                password = input(f"[LOGIN] {CLIENT}: Password - ")
                msg = "|".join([email, password])
                Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.LOGIN_USER, msg.encode())
            elif int(cmd) == MessageType.CREATE_USER:
                # ДОБАВИТЬ ПРОВЕРКУ НА АТОРИЗОВАННОСТЬ
                email = input(f"[SIGNUP] {CLIENT}: Email - ")
                password = input(f"[SIGNUP] {CLIENT}: Password - ")
                username = input(f"[SIGNUP] {CLIENT}: Username - ")
                msg = "|".join([email, password, username])
                Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.CREATE_USER, msg.encode())
            elif int(cmd) == MessageType.LOGOUT_USER:
                Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.LOGOUT_USER, OK_FLAG)
            elif int(cmd) == MessageType.CHAT:
                msg = input(f"[CHAT] {CLIENT}: Send message - ")
                Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.CHAT, msg.encode())

            elif int(cmd) == MessageType.UPDATE_CHAT:
                Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.UPDATE_CHAT, START_FLAG)
            # msg = input("[ACTION]: MSG - ")
            # Message.send_message_tcp(self._tcp_client_socket, MessageType.ECHO, cmd.encode('utf-8'))

    def send_get_room_list(self):
        Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.GET_ROOM_LIST, OK_FLAG)

    def send_get_client_list(self):
        Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.GET_CLIENT_LIST, OK_FLAG)

    def send_create_user(self, email, password, username):
        msg = "|".join([email, password, username])
        print(msg)
        Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.CREATE_USER, msg.encode())

    def send_login_user(self, email, password):
        msg = "|".join([email, password])
        Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.LOGIN_USER, msg.encode())

    def send_logout_user(self):
        Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.LOGOUT_USER, OK_FLAG)

    def send_update_chat(self):
        Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.UPDATE_CHAT, START_FLAG)

    def send_leave_room(self):
        self._active_room = None
        Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.LEAVE_ROOM, OK_FLAG)

    def send_join_room(self, room_name):
        Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.JOIN_ROOM, room_name.encode('utf-8'))

    def send_delete_room(self, room_name):
        Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.DELETE_ROOM, room_name.encode('utf-8'))

    def send_create_room(self, room_name):
        # room_name = input(f"[INPUT] {CLIENT}: Room name to create - ")
        Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.CREATE_ROOM, room_name.encode('utf-8'))

    def send_screenshare(self):
        threading.Thread(target=self.handle_screen_cmd).start()

    def send_video(self):
        threading.Thread(target=self.handle_video_cmd).start()

    def send_audio(self):
        threading.Thread(target=self.handle_audio_cmd).start()

    def send_chat(self, message):
        print("msg")
        Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.CHAT, message.encode())

    def send_echo(self):
        threading.Thread(target=Message.send_message_tcp,
                         args=(self._cmd_tcp_client_socket, MessageType.ECHO, "Hello".encode('utf-8'),)).start()

    def handle_screen_cmd(self):
        if self._is_screen_stream:
            self._is_screen_stream = False
            Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.SCREENSHARE, STOP_FLAG)
            print(f"[ACTION] {CLIENT}: Video stream was stopped")
        else:
            self._is_screen_stream = True
            Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.SCREENSHARE, START_FLAG)
            print(f"[ACTION] {CLIENT}: Video stream was started")
            self.handle_screen_stream()

    def handle_screen_stream(self):
        with mss.mss() as sct:
            # Можно выбрать конкретный монитор, указав его номер в параметре monitor
            monitor = sct.monitors[2]
            width = monitor["width"]
            height = monitor["height"]
            # Формируем словарь с параметрами для создания окна
            window_dict = {"top": monitor["top"], "left": monitor["left"], "width": width, "height": height}
            # Бесконечный цикл для получения и отправки изображений
            while True:
                # Снимаем скриншот экрана и конвертируем его в numpy array
                img = np.array(sct.grab(window_dict))
                # Конвертируем изображение из формата BGR в RGB
                # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                # Сжимаем изображение в формат JPEG
                _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 80])

                # Message.send_large_message_udp(self._screen_udp_client_socket, MessageType.SCREENSHARE,
                #                                buffer.tobytes(),
                #                                MAIN_SERVER_ADDRESS_CL, self._screen_udp_server_port)
                Message.send_large_message_udp_by_id(self._screen_udp_client_socket, buffer.tobytes(),
                                                     MAIN_SERVER_ADDRESS_CL, self._screen_udp_server_port,
                                                     self._udp_id_to_send)
                # Отправляем изображение по сокету
                # sock.sendall(buffer)
                # Ждем 0.1 секунду перед следующим снимком экрана
                time.sleep(0.01)

    def handle_video_cmd(self):
        if self._is_video_stream:
            self._is_video_stream = False
            # self.toggle_stream.emit(self._is_video_stream)
            Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.VIDEO, STOP_FLAG)
            print(f"[ACTION] {CLIENT}: Video stream was stopped")
        else:
            self._is_video_stream = True
            # self.toggle_stream.emit(self._is_video_stream)
            Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.VIDEO, START_FLAG)
            print(f"[ACTION] {CLIENT}: Video stream was started")
            self.handle_video_stream()
            # threading.Thread(target=self.handle_video_stream).start()

    def handle_video_stream(self):
        # Инициализация видео захвата
        capture = cv2.VideoCapture(0)
        while self._is_video_stream:
            # Чтение кадра
            ret, frame = capture.read()

            encoded, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])

            # Message.send_large_message_udp(self._video_udp_client_socket, MessageType.VIDEO, buffer.tobytes(),
            #                                MAIN_SERVER_ADDRESS_CL,
            #                                self._video_udp_server_port)
            # print(buffer.tobytes())
            Message.send_large_message_udp_by_id(self._video_udp_client_socket,  buffer.tobytes(),
                                           MAIN_SERVER_ADDRESS_CL,
                                           self._video_udp_server_port, self._udp_id_to_send)
        capture.release()

    def handle_audio_cmd(self):
        if self._is_audio_stream:
            self._is_audio_stream = False
            Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.AUDIO, STOP_FLAG)
            print(f"[ACTION] {CLIENT}: Audio stream was stopped")
        else:
            self._is_audio_stream = True
            Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.AUDIO, START_FLAG)
            print(f"[ACTION] {CLIENT}: Audio stream was started")
            # threading.Thread(target=self.handle_audio_stream).start()
            self.handle_audio_stream()

    def handle_audio_stream(self):
        self._audio.in_stream_audio()
        while self._is_audio_stream:
            # считываем аудио-данные из микрофона
            audio_data = self._audio.in_stream.read(AUDIO_CHUNK_SIZE)
            compressed_data = zlib.compress(audio_data)
            # отправляем закодированные данные на сервер
            Message.send_message_udp(self._voice_udp_client_socket, MessageType.AUDIO, compressed_data,
                                     MAIN_SERVER_ADDRESS_CL,
                                     self._voice_udp_server_port)
        # self._audio.close_in_stream()

    def get_user_by_id(self, user_id):
        print(f"user id - - - {type(user_id)}{user_id}")
        for user in self._users_in_room:
            if user.user_id == user_id:
                return user
        return None

    def handle_message(self):
        while True:
            message_type, message_data = Message.receive_message_tcp(self._cmd_tcp_client_socket)
            # вызываем обработчик для полученного сообщения
            if int(message_type) == MessageType.ECHO:
                print(f"[RECEIVED] {CLIENT} Message - {message_data}")

            elif int(message_type) == MessageType.VIDEO:
                print(f"user_list: {self._users_in_room}")
                msg = message_data.decode().split("|")
                print(f"message - {msg}")
                user = self.get_user_by_id(int(msg[1]))
                print(f"user - {user}")
                if user:
                    if msg[0] == START_FLAG.decode():
                        user.is_video_stream = True
                        self.user_is_video_stream.emit(True, user.username, user.user_id)
                        print(f"[INFO] {CLIENT} User {user.username} started video stream!")
                        threading.Thread(target=self.receive_video, args=(user.user_id,)).start()
                    elif msg[0] == STOP_FLAG.decode():
                        user.is_video_stream = False
                        self.user_is_video_stream.emit(False, user.username, user.user_id)
                        print(f"[INFO] {CLIENT} User {user.username} stopped video stream!")

            elif int(message_type) == MessageType.SCREENSHARE:
                msg = message_data.decode().split("|")
                user = self.get_user_by_id(int(msg[1]))
                if user:
                    if msg[0] == START_FLAG.decode():
                        # self._is_screen_stream = True
                        self.user_is_screen_stream.emit(True, user.username, user.user_id)
                        user.is_screen_stream = True
                        print(f"[INFO] {CLIENT} User {user.username} started screen stream!")
                        threading.Thread(target=self.receive_screen, args=(user.user_id,)).start()
                    elif msg[0] == STOP_FLAG.decode():
                        self.user_is_screen_stream.emit(False, user.username, user.user_id)
                        user.is_screen_stream = False
                        print(f"[INFO] {CLIENT} User {user.username} stopped screen stream!")

            elif int(message_type) == MessageType.AUDIO:
                print(f"user_list: {self._users_in_room}")
                msg = message_data.decode().split("|")
                print(f"message - {msg}")
                user = self.get_user_by_id(int(msg[1]))
                print(f"user - {user}")
                if user:
                    print("user is True")
                    if msg[0] == START_FLAG.decode():
                        self.user_is_voice_stream.emit(True, user.username)
                        user.is_voice_stream = True
                        print(f"[INFO] {CLIENT} User {user.username} started voice stream!")
                        threading.Thread(target=self.receive_audio, args=(user.username,)).start()
                    elif msg[0] == STOP_FLAG.decode():
                        self.user_is_voice_stream.emit(False, user.username)
                        user.is_screen_stream = False
                        print(f"[INFO] {CLIENT} User {user.username} stopped voice stream!")

            elif int(message_type) == MessageType.CREATE_ROOM:
                msg = message_data.decode().split("|")
                if msg[0] == OK_FLAG.decode():
                    print(type(msg[1]))
                    self._room_name_list.append(msg[1])
                    self._active_room = msg[1]
                    self.update_room_list.emit(self._room_name_list)
                    self.update_active_room.emit(self._active_room)
                    print(f"[SUCCESS] {CLIENT}: The room was created successfully!")
                elif msg[0] == ERROR_FLAG.decode():
                    print(f"[ERROR] {CLIENT}: Cant create the room")

            elif int(message_type) == MessageType.DELETE_ROOM:
                msg = message_data.decode().split("|")
                if msg[0] == OK_FLAG.decode():
                    self._room_name_list.remove(msg[1])
                    self._active_room = None
                    self.update_room_list.emit(self._room_name_list)
                    self.update_active_room.emit(self._active_room) # ERROR?
                    print(f"[SUCCESS] {CLIENT}: The room was deleted successfully!")
                elif msg[0] == ERROR_FLAG.decode():
                    print(f"[ERROR] {CLIENT}: Cant delete the room")

            elif int(message_type) == MessageType.JOIN_ROOM:
                msg = message_data.decode().split("|")
                if msg[0] == OK_FLAG.decode():
                    self._active_room = msg[1]
                    self.update_active_room.emit(self._active_room)
                    print(f"[SUCCESS] {CLIENT}: U re in room {msg[1]}")
                elif msg[0] == ERROR_FLAG.decode():
                    print(f"[ERROR] {CLIENT}: Cant create the room")

            elif int(message_type) == MessageType.GET_ROOM_LIST:
                self._room_name_list = message_data.decode().split("|")
                self.update_room_list.emit(self._room_name_list)
                print(f"[INFO] {CLIENT} Room list: {self._room_name_list}")

            elif int(message_type) == MessageType.GET_CLIENT_LIST:
                msg = message_data.decode().split("|")
                if msg[0] == ERROR_FLAG.decode():
                    print(f"[INFO] {CLIENT} You are not in room")
                else:
                    users = message_data.decode().split("|")
                    for i in range(0, len(users), 2):
                        user_id = int(users[i])
                        username = users[i + 1]
                        # Проверяем, есть ли пользователь уже в списке
                        if not any(user.user_id == user_id for user in self._users_in_room):
                            user = User(user_id, username)
                            self._users_in_room.append(user)
                    # self._users_in_room = message_data.decode().split("|")
                    print(f"[INFO] {CLIENT} Users list: {self._users_in_room}")
                    for user in self._users_in_room:
                        print(f"{user.user_id} - {user.username}")
                    self.update_user_list.emit([user.username for user in self._users_in_room])

            elif int(message_type) == MessageType.LOGIN_USER:
                msg = message_data.decode().split("|")
                print(msg)
                if msg[0] == ERROR_FLAG.decode():
                    print(f"[INFO] {CLIENT} Invalid email or password. Try again")
                    self.update_is_authorized.emit(False)
                    self._is_authorized = False
                elif msg[0] == OK_FLAG.decode():
                    self._email = msg[1]
                    self._password = msg[2]
                    self._username = msg[3]
                    self.update_is_authorized.emit(True)
                    self.update_email.emit(msg[1])
                    self.update_username.emit(msg[3])
                    self._is_authorized = True
                    print(f"[INFO] {CLIENT} U re welcome - {self._username}")

            elif int(message_type) == MessageType.CREATE_USER:
                msg = message_data.decode().split("|")
                if msg[0] == ERROR_FLAG.decode():
                    self._is_authorized = False
                    self.update_is_authorized.emit(False)
                    print(f"[INFO] {CLIENT} Current email is occupied. Try again")
                elif msg[0] == OK_FLAG.decode():
                    self._email = msg[1]
                    self._password = msg[2]
                    self._username = msg[3]
                    self._is_authorized = True
                    self.update_is_authorized.emit(True)
                    self.update_is_authorized.emit(True)
                    self.update_email.emit(msg[1])
                    self.update_username.emit(msg[3])
                    print(f"[INFO] {CLIENT} U re welcome")

            elif int(message_type) == MessageType.LOGOUT_USER:
                self._is_authorized = False
                self.update_is_authorized.emit(False)
                print(f"[INFO] {CLIENT} Logout status - {message_data.decode()}")

            elif int(message_type) == MessageType.CHAT:
                msg = message_data.decode().split("|")
                chat_msg = ChatMessage(chat_message_id=int(msg[0]), message_time=msg[1], message=msg[2],
                                       user=self.get_user_by_id(int(msg[3])))
                self._chat.append(chat_msg)
                self.update_message.emit([chat_msg.user.username, chat_msg.message_time, chat_msg.message])
                print(f"[CHAT] {CLIENT} {chat_msg.user}: [{chat_msg.message_time}] {chat_msg.message}")

            elif int(message_type) == MessageType.UPDATE_CHAT:
                msg = message_data.decode().split("|")
                if msg[0] == STOP_FLAG.decode():
                    print(f"[CHAT] {CLIENT} msgs in chat - {len(self._chat)}")
                    self.sort_chat()
                    print(f"[CHAT] {CLIENT} msgs in chat after sort - {len(self._chat)}")
                    self.update_whole_chat.emit([[m.user.username, m.message_time, m.message] for m in self._chat])
                    self.print_chat()
                    print(f"[CHAT] {CLIENT} chat printed")
                    continue
                elif msg[0] == START_FLAG.decode():
                    self._chat = []
                    print(f"[CHAT] {CLIENT} chat is empty")
                    continue
                user = self.get_user_by_id(int(msg[3]))
                chat_msg = ChatMessage(chat_message_id=int(msg[0]), message_time=msg[1], message=msg[2], user=user)
                print(f"[CHAT] {CLIENT} append msg to chat - {chat_msg}")
                self._chat.append(chat_msg)

    def print_chat(self):
        if len(self._chat):
            for msg in self._chat:
                message = msg.get_info_list_client()
                print(f"[CHAT] {CLIENT} {message}")

    def sort_chat(self):
        self._chat.sort(key=lambda msg: msg.chat_message_id)

    def receive_audio(self, username):
        self._audio.out_stream_audio()
        while self._show_other_audio_stream:
            data = Message.receive_message_udp(self._voice_udp_client_socket)
            if data[0] == MessageType.AUDIO:
                # print(f"[AUDIO_HANDLER] {SERVER}: {data}")
                data = zlib.decompress(data[1])
                # Проигрываем декодированное аудио
                self._audio.out_stream.write(data)
        # self._audio.close_out_stream()

    def receive_screen(self, user_id):
        while self._show_other_screen_stream:
            # data = Message.receive_large_message_udp(self._screen_udp_client_socket)
            data = Message.receive_large_message_udp_by_id(self._screen_udp_client_socket, user_id)
            # if data[0] == MessageType.SCREENSHARE:
            try:
                # попытаться выполнить декодирование изображения
                frame = cv2.imdecode(np.frombuffer(data[0], dtype=np.uint8), cv2.IMREAD_COLOR)
            except cv2.error as e:
                # обработать исключение и перейти к следующему изображению
                print(f"Пропущено неправильное изображение: {e}")
            # frame = cv2.imdecode(np.frombuffer(data[0], dtype=np.uint8), cv2.IMREAD_COLOR)
            # self.frame_received.emit(frame)
            if frame.any():
                self.update_screen_frame.emit(frame, user_id)
                # cv2.imshow('Video Frame', frame)
                # if cv2.waitKey(1) == ord('q'):
                # Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.SCREENSHARE, STOP_FLAG)
                #     break
        # cv2.destroyAllWindows()

    def receive_video(self, user_id):
        while self._show_other_video_stream:
            # data = Message.receive_large_message_udp(self._video_udp_client_socket)
            data = Message.receive_large_message_udp_by_id(self._video_udp_client_socket, user_id)
            # print(data)
            try:
                # попытаться выполнить декодирование изображения
                frame = cv2.imdecode(np.frombuffer(data[0], dtype=np.uint8), cv2.IMREAD_COLOR)
            except cv2.error as e:
                # обработать исключение и перейти к следующему изображению
                print(f"Пропущено неправильное изображение: {e}")
            # frame = cv2.imdecode(np.frombuffer(data[0], dtype=np.uint8), cv2.IMREAD_COLOR)
            # self.frame_received.emit(frame)
            if frame.any():
                self.update_video_frame.emit(frame, user_id)
                    # print(frame)
                    # cv2.imshow('Video Frame', frame)
                    # if cv2.waitKey(1) == ord('q'):
                    #     Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.VIDEO, STOP_FLAG)
                    # break
            # cv2.destroyAllWindows()

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        self._email = value

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value

    def get_users_in_room(self):
        return self._users_in_room

    def connect(self):
        pass

    def disconnect(self):
        pass

    def send_message(self):
        pass

    def start_screen_share(self):
        pass

    def stop_screen_share(self):
        pass
