import socket
import time

from consts import *


class NetworkManager:
    def __init__(self, udp_server_port=UDP_SERVER_PORT, tcp_server_port=MAIN_TCP_SERVER_PORT, server_address=MAIN_SERVER_ADDRESS):
        self._udp_server_port = udp_server_port
        self._tcp_server_port = tcp_server_port
        self._server_address = server_address
        self._client_sockets = []
        self._udp_client_sockets = {}
        self._tcp_client_sockets = {}
        self._udp_server_socket = None
        self._tcp_server_socket = None
        self._is_tcp_connected = False
        self._is_udp_connected = False
        # self._tcp_server_socket = self.start_tcp_server()

    def connect_to_server(self):
        client_id = len(self._tcp_client_sockets)
        if len(self._udp_client_sockets) != client_id:
            print(f"[ERROR] {NETWORK_MANAGER} TCP clients count: {client_id}\n\tUDP clients count: {len(self._udp_client_sockets)}")
        elif self._is_tcp_connected and self._is_udp_connected:
            self.connect_to_tcp_server(client_id)
            self.connect_to_udp_server(client_id)
        else:
            print(f"[ERROR] {NETWORK_MANAGER} TCP connection flag: {self._is_tcp_connected}\n\tUDP connection flag: {self._is_udp_connected}")

    def connect_to_udp_server(self, client_id):
        udp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._udp_client_sockets[client_id] = udp_client_socket
        print(f"[OK] {NETWORK_MANAGER} Client connected to UDP server\n\tSocket: {udp_client_socket}")

    def connect_to_tcp_server(self, client_id):
        tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to the server
        server_address = (MAIN_SERVER_ADDRESS, MAIN_TCP_SERVER_PORT)
        # self._tcp_server_socket.connect((SERVER_ADDRESS, TCP_SERVER_PORT))
        tcp_client_socket.connect(server_address) # FOR DIFF PCs
        self._tcp_client_sockets[client_id] = tcp_client_socket
        print(f"[OK] {NETWORK_MANAGER} Client connected to TCP server\n\tSocket: {tcp_client_socket}")

    def disconnect_from_server(self, client_id):
        self.close_udp_client_connection(client_id)
        self.close_tcp_client_connection(client_id)

    def close_udp_client_connection(self, client_id):
        self._udp_client_sockets[client_id].close()
        del self._udp_client_sockets[client_id]
        print(f"[OK] {NETWORK_MANAGER} UDP client '{client_id}' disconnected")

    def close_tcp_client_connection(self, client_id):
        self._tcp_client_sockets[client_id].close()
        del self._tcp_client_sockets[client_id]
        print(f"[OK] {NETWORK_MANAGER} TCP client '{client_id}' disconnected")

    def is_connected(self):
        pass
