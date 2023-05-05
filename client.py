import socket
from message import Message
from messageType import MessageType
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
        del self._udp_client_socket
        print(f"[OK] {CLIENT} UDP client disconnected")

    def close_tcp_client_connection(self):
        self._tcp_client_socket.close()
        print(f"[OK] {CLIENT} TCP client disconnected")

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