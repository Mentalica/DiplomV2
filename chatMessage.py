import datetime


class ChatMessage:
    def __init__(self, chat_id=None, chat_message_id=None, message=None, user=None,
                 message_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")):
        self._chat_id = chat_id
        self._chat_message_id = chat_message_id
        self._message_time = message_time
        self._message = message
        self._user = user

    def get_info_list(self):
        return [str(self._chat_message_id), self._message_time, self._message,
                str(self._user.user_id)]

    def get_info_list_client(self):
        return f"{self._user.username}: [{self._message_time}] {self._message}"

    @property
    def chat_id(self):
        return self._chat_id

    @chat_id.setter
    def chat_id(self, value):
        self._chat_id = value

    @property
    def chat_message_id(self):
        return self._chat_message_id

    @chat_message_id.setter
    def chat_message_id(self, value):
        self._chat_message_id = value

    @property
    def message_time(self):
        return self._message_time

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

