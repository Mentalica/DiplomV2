import socket
import threading
from networkManager import NetworkManager
from consts import *


class Server:
    def __init__(self, max_client=MAX_CLIENTS_COUNT):
        self._is_tcp_connected = False
        self._is_udp_connected = False
        self._tcp_server_socket = None
        self._udp_server_socket = None
        self._max_clients = max_client

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
        print(f"[OK] {NETWORK_MANAGER} UDP server started at {SERVER_ADDRESS}:{UDP_SERVER_PORT}\n\tSocket: "
              f"{self._udp_server_socket}")

    def create_tcp_socket(self):
        self._tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._tcp_server_socket.bind((SERVER_ADDRESS, TCP_SERVER_PORT))
        self._tcp_server_socket.listen(self._max_clients)
        self._is_tcp_connected = True
        print(f"[OK] {NETWORK_MANAGER} TCP server started at {SERVER_ADDRESS}:{TCP_SERVER_PORT}\n\tSocket: "
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
            print(f"[OK] {SERVER} Connection from {client_address} has been established! Client ID - {client_id}")
            # Handle the client connection in a separate thread
            client_thread = threading.Thread(target=self.handle_client, args=(client_id,))
            client_id += 1
            client_thread.start()

    def handle_client(self, client_id):
        pass

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



