import base64
import socket
import time
import threading
import zlib
import cv2
import numpy as np
import mss

import pyaudio
from message import Message
from messageType import MessageType
from audioRecorder import AudioRecorder
from consts import *
from PyQt5.QtCore import QObject, pyqtSignal

class Client(QObject):
    toggle_stream = pyqtSignal(bool)
    frame_received = pyqtSignal(np.ndarray)
    def __init__(self):
        super().__init__()
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
        self._users_in_room = []

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
            cmd = input(f"[ACTION-INPUT] {CLIENT} ({self._active_room}) Command number - ")
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
                Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.JOIN_ROOM,
                                         room_name.encode('utf-8'))
            elif int(cmd) == MessageType.LEAVE_ROOM:
                self._active_room = None
                Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.LEAVE_ROOM,
                                         OK_FLAG)
            elif int(cmd) == MessageType.GET_ROOM_LIST:
                Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.GET_ROOM_LIST,
                                         OK_FLAG)
            elif int(cmd) == MessageType.GET_CLIENT_LIST:
                Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.GET_CLIENT_LIST,
                                         OK_FLAG)

            # msg = input("[ACTION]: MSG - ")
            # Message.send_message_tcp(self._tcp_client_socket, MessageType.ECHO, cmd.encode('utf-8'))
    def send_command_ui(self, cmd):
        # while True:
        #     time.sleep(0.1)  # STILL I HAVENT GUI
        #     cmd = input(f"[ACTION-INPUT] {CLIENT}: Command number - ")
        if int(cmd) == MessageType.ECHO:
            threading.Thread(target=Message.send_message_tcp,
                             args=(self._cmd_tcp_client_socket, MessageType.ECHO, cmd.encode('utf-8'),)).start()
        elif int(cmd) == MessageType.AUDIO:
            threading.Thread(target=self.handle_audio_cmd).start()
        elif int(cmd) == MessageType.VIDEO:
            threading.Thread(target=self.handle_video_cmd).start()
        elif int(cmd) == MessageType.SCREENSHARE:
            threading.Thread(target=self.handle_screen_cmd).start()

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

                Message.send_large_message_udp(self._screen_udp_client_socket, MessageType.SCREENSHARE, buffer.tobytes(),
                                               MAIN_SERVER_ADDRESS_CL, self._screen_udp_server_port)
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

            Message.send_large_message_udp(self._video_udp_client_socket, MessageType.VIDEO, buffer.tobytes(),
                                           MAIN_SERVER_ADDRESS_CL,
                                           self._video_udp_server_port)
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

    def handle_message(self):
        while True:
            message_type, message_data = Message.receive_message_tcp(self._cmd_tcp_client_socket)
            # вызываем обработчик для полученного сообщения
            if int(message_type) == MessageType.ECHO:
                print(f"[RECEIVED] {CLIENT}: Message - {message_data}")
            elif int(message_type) == MessageType.VIDEO:
                if message_data == START_FLAG:
                # self._is_screen_stream = True
                    self._show_other_video_stream = True # need to be realized in another method !!!!!!!!!
                    threading.Thread(target=self.receive_video).start()
                elif message_data == STOP_FLAG:
                    self._show_other_video_stream = False
            elif int(message_type) == MessageType.SCREENSHARE:
                if message_data == START_FLAG:
                # self._is_screen_stream = True
                    self._show_other_screen_stream = True # need to be realized in another method !!!!!!!!!
                    threading.Thread(target=self.receive_screen).start()
                elif message_data == STOP_FLAG:
                    self._show_other_screen_stream = False
            elif int(message_type) == MessageType.AUDIO:
                if message_data == START_FLAG:
                # self._is_screen_stream = True
                    self._show_other_audio_stream = True # need to be realized in another method !!!!!!!!!
                    threading.Thread(target=self.receive_audio).start()
                elif message_data == STOP_FLAG:
                    self._show_other_audio_stream = False
            elif int(message_type) == MessageType.CREATE_ROOM:
                msg = message_data.decode().split("|")
                if msg[0] == OK_FLAG.decode():
                    print(type(msg[1]))
                    self._room_name_list.append(msg[1])
                    self._active_room = msg[1]
                    print(f"[SUCCESS] {CLIENT}: The room was created successfully!")
                elif msg[0] == ERROR_FLAG.decode():
                    print(f"[ERROR] {CLIENT}: Cant create the room")
            elif int(message_type) == MessageType.DELETE_ROOM:
                msg = message_data.decode().split("|")
                if msg[0] == OK_FLAG.decode():
                    self._room_name_list.remove(msg[1])
                    self._active_room = None
                    print(f"[SUCCESS] {CLIENT}: The room was deleted successfully!")
                elif msg[0] == ERROR_FLAG.decode():
                    print(f"[ERROR] {CLIENT}: Cant delete the room")
            elif int(message_type) == MessageType.JOIN_ROOM:
                msg = message_data.decode().split("|")
                if msg[0] == OK_FLAG.decode():
                    self._active_room = msg[1]
                    print(f"[SUCCESS] {CLIENT}: U re in room {msg[1]}")
                elif msg[0] == ERROR_FLAG.decode():
                    print(f"[ERROR] {CLIENT}: Cant create the room")
            elif int(message_type) == MessageType.GET_ROOM_LIST:
                self._room_name_list = message_data.decode().split("|")
                print(f"[INFO] {CLIENT} Room list: {self._room_name_list}")
            elif int(message_type) == MessageType.GET_CLIENT_LIST:
                if msg[0] == ERROR_FLAG.decode():
                    print(f"[INFO] {CLIENT} U re not in room")
                else:
                    self._users_in_room = message_data.decode().split("|")
                    print(f"[INFO] {CLIENT} Users list: {self._users_in_room}")

    def receive_audio(self):
        self._audio.out_stream_audio()
        while self._show_other_audio_stream:
            data = Message.receive_message_udp(self._voice_udp_client_socket)
            if data[0] == MessageType.AUDIO:
                # print(f"[AUDIO_HANDLER] {SERVER}: {data}")
                data = zlib.decompress(data[1])
                # Проигрываем декодированное аудио
                self._audio.out_stream.write(data)
        # self._audio.close_out_stream()

    def receive_screen(self):
        while self._show_other_screen_stream:
            data = Message.receive_large_message_udp(self._screen_udp_client_socket)
            if data[0] == MessageType.SCREENSHARE:
                frame = cv2.imdecode(np.frombuffer(data[1], dtype=np.uint8), cv2.IMREAD_COLOR)
                self.frame_received.emit(frame)
                # cv2.imshow('Video Frame', frame)
                # if cv2.waitKey(1) == ord('q'):
                    # Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.SCREENSHARE, STOP_FLAG)
                    # break
        # cv2.destroyAllWindows()

    def receive_video(self):
        while self._show_other_video_stream:
            data = Message.receive_large_message_udp(self._video_udp_client_socket)
            if data[0] == MessageType.VIDEO:
                frame = cv2.imdecode(np.frombuffer(data[1], dtype=np.uint8), cv2.IMREAD_COLOR)
                self.frame_received.emit(frame)
                # print(frame)
                # cv2.imshow('Video Frame', frame)
                # if cv2.waitKey(1) == ord('q'):
                #     Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.VIDEO, STOP_FLAG)
                    # break
        # cv2.destroyAllWindows()

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
