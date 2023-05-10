import socket
from typing import List

# from room import Room

class User:
    def __init__(self, user_id=None, username="", password=None, email=None, main_tcp_socket_client=None,
                 address=None, screen_udp_port_client=None, cmd_tcp_port_client=None, voice_udp_port_client=None,
                 video_udp_port_client=None, cmd_tcp_port_server=None, screen_udp_port_server=None,
                 voice_udp_port_server=None, video_udp_port_server=None, main_tcp_port=None):
        self._user_id = user_id
        self._username = username
        self._password = password
        self._email = email
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
        # Flags
        self._is_screen_stream = False
        self._is_voice_stream = False
        self._is_video_stream = False


        # self._room_list: List[Room] = []
        # self._active_room: Room = None
        self._room_list = []
        self._active_room = None
        # later
        self._is_online = None  # Later
        self._is_muted = None  # Later
        self._is_deafened = None  # Later
        self._room = None  # Later



    def get_room_list(self):
        return self._room_list

    def add_room_to_list(self, value):
        self._room_list.append(value)

    def delete_room(self, room):
        # self._room_list = [r for r in self._room_list if r != room]
        for r in self._room_list:
            if r == room:
                self._room_list.remove(r)
                break

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

    @property
    def active_room(self):
        return self._active_room

    @active_room.setter
    def active_room(self, value):
        self._active_room = value

    @property
    def is_screen_stream(self):
        return self._is_screen_stream

    @is_screen_stream.setter
    def is_screen_stream(self, value):
        self._is_screen_stream = value

    @property
    def is_video_stream(self):
        return self._is_video_stream

    @is_video_stream.setter
    def is_video_stream(self, value):
        self._is_video_stream = value

    @property
    def is_voice_stream(self):
        return self._is_voice_stream

    @is_voice_stream.setter
    def is_voice_stream(self, value):
        self._is_voice_stream = value

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

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, value):
        self._user_id = value







