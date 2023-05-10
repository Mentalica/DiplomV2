import socket
from typing import List

# from room import Room

class NetworkManager:
    def __init__(self, main_tcp_socket_client=None, address=None, screen_udp_port_client=None, cmd_tcp_port_client=None,
                 voice_udp_port_client=None, video_udp_port_client=None, cmd_tcp_port_server=None,
                 screen_udp_port_server=None, voice_udp_port_server=None, video_udp_port_server=None,
                 main_tcp_port=None, user=None, network_manager_id=None):
        self._network_manager_id = network_manager_id
        self._user = user
        self._main_tcp_port = main_tcp_port
        self._address = address
        # server ports
        self._cmd_tcp_port_server = cmd_tcp_port_server
        self._screen_udp_port_server = screen_udp_port_server
        self._voice_udp_port_server = voice_udp_port_server
        self._video_udp_port_server = video_udp_port_server
        # client ports
        self._cmd_tcp_port_client = cmd_tcp_port_client
        self._screen_udp_port_client = screen_udp_port_client
        self._voice_udp_port_client = voice_udp_port_client
        self._video_udp_port_client = video_udp_port_client
        # server sockets
        # self._main_tcp_socket = main_tcp_socket
        self._cmd_tcp_socket_server = None
        self._screen_udp_socket_server = None
        self._voice_udp_socket_server = None
        self._video_udp_socket_server = None
        # client sockets
        self._main_tcp_socket_client = main_tcp_socket_client
        self._cmd_tcp_socket_client = None
        # self._room_list: List[Room] = []
        # self._active_room: Room = None

        # later
        self._is_online = None  # Later
        self._is_muted = None  # Later
        self._is_deafened = None  # Later

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        self._user = value

    @property
    def network_manager_id(self):
        return self._network_manager_id

    @network_manager_id.setter
    def network_manager_id(self, value):
        self._network_manager_id = value

    @property
    def cmd_tcp_socket_client(self):
        return self._cmd_tcp_socket_client

    @cmd_tcp_socket_client.setter
    def cmd_tcp_socket_client(self, value):
        self._cmd_tcp_socket_client = value

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, new_address):
        self._address = new_address

    @property
    def cmd_tcp_socket_server(self):
        return self._cmd_tcp_socket_server

    @cmd_tcp_socket_server.setter
    def cmd_tcp_socket_server(self, value):
        self._cmd_tcp_socket_server = value

    @property
    def screen_udp_socket_server(self):
        return self._screen_udp_socket_server

    @screen_udp_socket_server.setter
    def screen_udp_socket_server(self, value):
        self._screen_udp_socket_server = value

    @property
    def voice_udp_socket_server(self):
        return self._voice_udp_socket_server

    @voice_udp_socket_server.setter
    def voice_udp_socket_server(self, value):
        self._voice_udp_socket_server = value

    @property
    def video_udp_socket_server(self):
        return self._video_udp_socket_server

    @video_udp_socket_server.setter
    def video_udp_socket_server(self, value):
        self._video_udp_socket_server = value

    @property
    def cmd_tcp_port_server(self):
        return self._cmd_tcp_port_server

    @cmd_tcp_port_server.setter
    def cmd_tcp_port_server(self, value):
        self._cmd_tcp_port_server = value

    @property
    def screen_udp_port_server(self):
        return self._screen_udp_port_server

    @screen_udp_port_server.setter
    def screen_udp_port_server(self, value):
        self._screen_udp_port_server = value

    @property
    def voice_udp_port_server(self):
        return self._voice_udp_port_server

    @voice_udp_port_server.setter
    def voice_udp_port_server(self, value):
        self._voice_udp_port_server = value

    @property
    def video_udp_port_server(self):
        return self._video_udp_port_server

    @video_udp_port_server.setter
    def video_udp_port_server(self, value):
        self._video_udp_port_server = value

    @property
    def cmd_tcp_port_client(self):
        return self._cmd_tcp_port_client

    @cmd_tcp_port_client.setter
    def cmd_tcp_port_client(self, value):
        self._cmd_tcp_port_client = value

    @property
    def screen_udp_port_client(self):
        return self._screen_udp_port_client

    @screen_udp_port_client.setter
    def screen_udp_port_client(self, value):
        self._screen_udp_port_client = value

    @property
    def voice_udp_port_client(self):
        return self._voice_udp_port_client

    @voice_udp_port_client.setter
    def voice_udp_port_client(self, value):
        self._voice_udp_port_client = value

    @property
    def video_udp_port_client(self):
        return self._video_udp_port_client

    @video_udp_port_client.setter
    def video_udp_port_client(self, value):
        self._video_udp_port_client = value








