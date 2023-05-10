


class User:
    def __init__(self, user_id=None, username=None, password=None, email=None, active_client=None):
        self._user_id = user_id
        self._username = username
        self._password = password
        self._email = email
        self._room_list = []
        self._active_room = None
        self._active_client = active_client
        # Flags
        self._is_screen_stream = False
        self._is_voice_stream = False
        self._is_video_stream = False
        self._is_online = False

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
    def is_online(self):
        return self._is_online

    @is_online.setter
    def is_online(self, value):
        self._is_online = value

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        self._email = value

    @property
    def active_client(self):
        return self._active_client

    @active_client.setter
    def active_client(self, value):
        self._active_client = value

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, value):
        self._user_id = value

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

