import base64
import socket
import time
import threading
import zlib
import cv2
import numpy as np

import pyaudio
from message import Message
from messageType import MessageType
from audioRecorder import AudioRecorder
from consts import *


class Client:
    def __init__(self):
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

        self._is_audio_stream = False
        self._is_video_stream = False

    def connect_to_server(self):
        self._main_tcp_client_socket = self.connect_to_tcp_server(MAIN_TCP_SERVER_PORT)

        msg_type, msg_data = Message.receive_message_tcp(self._main_tcp_client_socket)
        print(f"[inf] {CLIENT}: msg data: {msg_data}\nmsg type: {msg_type}\nsocket: {self._main_tcp_client_socket}")
        ports = msg_data.decode().split(" ")
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
        Message.send_message_udp(udp_client_socket, MessageType.ECHO, b"OK", MAIN_SERVER_ADDRESS, udp_server_port)
        msg = Message.receive_message_udp(udp_client_socket)
        if int(msg[0]) == MessageType.ECHO and msg[1].decode() == "OK":
            print(f"[OK] {CLIENT} Client connected to UDP server\n\tSocket: {udp_client_socket}")
        else:
            print(f"[ERROR] {CLIENT}: {msg}")
        return udp_client_socket

    def connect_to_tcp_server(self, tcp_port):
        tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to the server
        server_address = (MAIN_SERVER_ADDRESS, tcp_port)
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
            cmd = input(f"[ACTION-INPUT] {CLIENT}: Command number - ")
            if int(cmd) == MessageType.ECHO:
                threading.Thread(target=Message.send_message_tcp, args=(self._cmd_tcp_client_socket, MessageType.ECHO, cmd.encode('utf-8'),)).start()
            elif int(cmd) == MessageType.AUDIO:
                threading.Thread(target=self.handle_audio_cmd).start()
            elif int(cmd) == MessageType.VIDEO:
                threading.Thread(target=self.handle_video_cmd).start()

            # msg = input("[ACTION]: MSG - ")
            # Message.send_message_tcp(self._tcp_client_socket, MessageType.ECHO, cmd.encode('utf-8'))

    def handle_video_cmd(self):
        if self._is_video_stream:
            self._is_video_stream = False
            Message.send_message_tcp(self._cmd_tcp_client_socket, MessageType.VIDEO, STOP_FLAG)
            print(f"[ACTION] {CLIENT}: Video stream was stopped")
        else:
            self._is_video_stream = True
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
            # cv2.imshow('Video Frame', frame)
            # print(frame)
            encoded, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            # print(buffer)
            # message = base64.b64encode(buffer)

            # print(f"Len: {len(message)}data: {message}")
            # Message.send_message_udp(self._video_udp_client_socket, MessageType.VIDEO, message, MAIN_SERVER_ADDRESS,
            Message.send_message_udp(self._video_udp_client_socket, MessageType.VIDEO, buffer.tobytes(), MAIN_SERVER_ADDRESS,
                                     self._video_udp_server_port)
            # Message.send_large_message_udp(self._udp_client_socket, MessageType.VIDEO, message, SERVER_ADDRESS,
            #                                UDP_SERVER_PORT)

        # Остановка захвата видео и освобождение ресурсов
        capture.release()
        # cv2.destroyAllWindows()

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
        audio = AudioRecorder()
        audio.in_stream_audio()
        while self._is_audio_stream:
            # считываем аудио-данные из микрофона
            audio_data = audio.stream.read(AUDIO_CHUNK_SIZE)
            compressed_data = zlib.compress(audio_data)
            # отправляем закодированные данные на сервер
            Message.send_message_udp(self._voice_udp_client_socket, MessageType.AUDIO, compressed_data, MAIN_SERVER_ADDRESS,
                                     self._voice_udp_server_port)
        audio.close()

    def handle_message(self):
        while True:
            message_type, message_data = Message.receive_message_tcp(self._cmd_tcp_client_socket)
            # вызываем обработчик для полученного сообщения
            if int(message_type) == MessageType.ECHO:
                print(f"[RECEIVED] {CLIENT}: Message - {message_data}")
            elif int(message_type) == MessageType.AUDIO:
                pass

    def connect(self):
        pass

    def disconnect(self):
        pass

    def send_video(self):
        pass

    def send_audio(self):
        pass

    def send_message(self):
        pass

    def start_screen_share(self):
        pass

    def stop_screen_share(self):
        pass

    def receive_audio(self):
        pass

    def receive_video(self):
        pass

    def receive_message(self):
        pass
