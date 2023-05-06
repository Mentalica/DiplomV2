import socket
import time
import threading
import zlib

import pyaudio
from message import Message
from messageType import MessageType
from audioEncoder import AudioEncoder
from audioRecorder import AudioRecorder
from consts import *


class Client:
    def __init__(self):
        self._tcp_client_socket = None
        self._udp_client_socket = None

    def connect_to_server(self):
        self.connect_to_tcp_server()
        self.connect_to_udp_server()

    def connect_to_udp_server(self):
        udp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._udp_client_socket = udp_client_socket
        Message.send_message_udp(self._udp_client_socket, MessageType.ECHO, b"OK", SERVER_ADDRESS, UDP_SERVER_PORT)
        msg = Message.receive_message_udp(self._udp_client_socket)
        if int(msg[0]) == MessageType.ECHO and msg[1].decode() == "OK":
            print(f"[OK] {CLIENT} Client connected to UDP server\n\tSocket: {udp_client_socket}")
        else:
            print(f"[ERROR] {CLIENT}: {msg}")

    def connect_to_tcp_server(self):
        tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to the server
        server_address = (SERVER_ADDRESS, TCP_SERVER_PORT)
        # self._tcp_server_socket.connect((SERVER_ADDRESS, TCP_SERVER_PORT))
        tcp_client_socket.connect(server_address) # FOR DIFF PCs
        self._tcp_client_socket = tcp_client_socket
        print(f"[OK] {CLIENT} Client connected to TCP server\n\tSocket: {tcp_client_socket}")

    def disconnect_from_server(self):
        self.close_udp_client_connection()
        self.close_tcp_client_connection()

    def close_udp_client_connection(self):
        self._udp_client_socket.close()
        print(f"[OK] {CLIENT} UDP client disconnected")

    def close_tcp_client_connection(self):
        self._tcp_client_socket.close()
        print(f"[OK] {CLIENT} TCP client disconnected")

    def run(self):
        threading.Thread(target=self.send_command).start()
        threading.Thread(target=self.handle_message).start()
        # self.send_message()
        # self.handle_message()

    def send_command(self):
        while True:
            time.sleep(0.1) # STILL I HAVENT GUI
            cmd = input(f"[ACTION-INPUT] {CLIENT}: Command number - ")
            if int(cmd) == MessageType.AUDIO:
                Message.send_message_tcp(self._tcp_client_socket, MessageType.AUDIO, "".encode('utf-8'))
                print(f"[SEND_CMD] {CLIENT}: SUCCESS")
                self.handle_audio()
                threading.Thread(target=self.send_audio)

                print(f"[SEND_CMD] {CLIENT}: NOT SUCCESS")
            # msg = input("[ACTION]: MSG - ")
            # Message.send_message_tcp(self._tcp_client_socket, MessageType.ECHO, cmd.encode('utf-8'))

    def handle_message(self):
        while True:
            message_type, message_data = Message.receive_message_tcp(self._tcp_client_socket)
            # вызываем обработчик для полученного сообщения
            if int(message_type) == MessageType.ECHO:
                print(f"[RECEIVED] {CLIENT}: Message - {message_data}")
            elif int(message_type) == MessageType.AUDIO:
                pass

    def handle_audio(self):
        audio = AudioRecorder()
        audio.in_stream_audio()
        while True:
            print(f"[SEND_HANDLER] {CLIENT}: start")
            # считываем аудио-данные из микрофона
            audio_data = audio.stream.read(AUDIO_CHUNK_SIZE)
            compressed_data = zlib.compress(audio_data)
            # print(f"[SEND_HANDLER] {CLIENT}: {audio_data}")
            # кодируем аудио-данные в формат MP3
            # encoded_data = encoder.encode_to_mp3(audio_data)
            # encoded_data = encoder.encode_frame(audio_data)
            print(f"[SEND_HANDLER] {CLIENT}: Encoded data: {compressed_data}")
            # отправляем закодированные данные на сервер
            Message.send_message_udp(self._udp_client_socket, MessageType.AUDIO, compressed_data, SERVER_ADDRESS,
                                     UDP_SERVER_PORT)

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