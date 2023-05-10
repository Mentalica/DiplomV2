import datetime


class ChatMessage:
    def __init__(self, chat_message_id=None, message=None, user=None, time_str=None):
        self._chat_message_id = chat_message_id
        self._time_str = time_str
        self._message_time = None
        self._message_time = datetime.datetime.now()
        self._message = message
        self._user = user

    def get_info_list(self):
        return [str(self._chat_message_id), self._message_time.strftime("%Y-%m-%d %H:%M"), self._message,
                self._user.username]

    def get_info_list_client(self):
        return f"{self._user}: [{self._time_str}] {self._message}"

    @property
    def time_str(self):
        return self._time_str

    @time_str.setter
    def time_str(self, value):
        self._time_str = value

    @property
    def chat_message_id(self):
        return self._chat_message_id

    @chat_message_id.setter
    def chat_message_id(self, value):
        self._chat_message_id = value

    @property
    def message_time(self):
        return self._message_time.strftime("%Y-%m-%d %H:%M")

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        self._message = value

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        self._user = value

