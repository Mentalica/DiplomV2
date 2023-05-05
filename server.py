import socket
import struct
import threading
from messageType import MessageType
from message import Message
from networkManager import NetworkManager
from consts import *
from user import User


class Server:
    def __init__(self, max_client=MAX_CLIENTS_COUNT):
        self._is_tcp_connected = False
        self._is_udp_connected = False
        self._tcp_server_socket = None
        self._udp_server_socket = None
        self._max_clients = max_client
        self._clients = []

    def start(self):
        self.create_tcp_socket()
        self.create_udp_socket()

    def stop(self):
        self.close_tcp_server_connection()
        self.close_udp_server_connection()

    def create_udp_socket(self):
        self._udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._udp_server_socket.bind((SERVER_ADDRESS, UDP_SERVER_PORT))
        self._is_udp_connected = True
        print(f"[OK] {SERVER} UDP server started at {SERVER_ADDRESS}:{UDP_SERVER_PORT}\n\tSocket: "
              f"{self._udp_server_socket}")

    def create_tcp_socket(self):
        self._tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._tcp_server_socket.bind((SERVER_ADDRESS, TCP_SERVER_PORT))
        self._tcp_server_socket.listen(self._max_clients)
        self._is_tcp_connected = True
        print(f"[OK] {SERVER} TCP server started at {SERVER_ADDRESS}:{TCP_SERVER_PORT}\n\tSocket: "
              f"{self._tcp_server_socket}")

    def close_udp_server_connection(self):
        self._udp_server_socket.close()
        self._is_udp_connected = False
        print(f"[OK] {SERVER} UDP server was stopped")

    def close_tcp_server_connection(self):
        self._tcp_server_socket.close()
        self._is_tcp_connected = False
        print(f"[OK] {SERVER} TCP server was stopped")

    def accept_connection(self):
        client_id = 0
        while True:
            # Wait for a client to connect
            client_socket, client_address = self._tcp_server_socket.accept()
            print(f"[OK] {SERVER} TCP connection from {client_address} has been established! Client ID - {client_id}")

            # Test UDP conn

            msg = Message.receive_message_udp(self._udp_server_socket)
            if int(msg[0]) == MessageType.ECHO and msg[1].decode() == "OK":
                # print(f"[OK] {SERVER} Client UDP checked")
                # print(f"[OK] {SERVER} UDP connection from ({msg[1]}, {msg[2]}) has been established! Client ID - {client_id}")
                print(f"[OK] {SERVER} UDP connection from {msg[2]} has been established! Client ID - {client_id}")
            else:
                print(f"[ERROR] {SERVER}: {msg[0]}\n{type(msg[0])}")
            Message.send_message_udp(self._udp_server_socket, MessageType.ECHO, b"OK", client_address[0], msg[2][1])
            # Add user in list
            new_client = User(user_id=client_id, tcp_socket=client_socket, address=client_address[0],
                              udp_port=msg[2][1], tcp_port=client_address[1])
            self._clients.append(new_client)

            # Handle the client connection in a separate thread
            client_thread = threading.Thread(target=self.handle_client, args=(new_client,))
            client_id += 1
            client_thread.start()

    def handle_client(self, client: User):
        while True:
            # Принимаем сообщение от клиента
            message_type, message_data = Message.receive_message_tcp(client.get_tcp_socket())
            print(f"[RECEIVED] {SERVER}: msg_type - {message_type}; client ID - {client.get_user_id()}"
                  f"\n\tmsg_data: {message_data}")
            # Обрабатываем сообщение в зависимости от его типа
            if message_type == MessageType.ECHO:
                # Обработка command-сообщения
                Message.send_message_tcp(client.get_tcp_socket(), MessageType.ECHO, b"Hello there")
            elif message_type == MessageType.CHAT:
                # Обработка чат-сообщения
                ...
            elif message_type == MessageType.VIDEO:
                # Обработка видео-сообщения
                ...
            elif message_type == MessageType.AUDIO:
                # Обработка аудио-сообщения
                ...
            elif message_type == MessageType.SCREENSHARE:
                # Обработка сообщения демонстрации экрана
                ...
            else:
                # Неизвестный тип сообщения
                ...

    def create_room(self):
        pass

    def delete_room(self):
        pass

    def broadcast_message(self):
        pass

    def get_room_users(self):
        pass

    def get_all_rooms(self):
        pass



