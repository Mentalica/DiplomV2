from typing import List

from chatMessage import ChatMessage


class Chat:
    def __init__(self, chat_id=None, room=None, chat_messages=[]):
        self._chat_id = chat_id
        self._room = room
        self._chat_messages: List[ChatMessage] = chat_messages

    def get_msg_chat_id(self):
        if len(self._chat_messages) == 0:
            return 0
        else:
            return self._chat_messages[-1].chat_message_id + 1

    def get_chat_messages(self):
        return self._chat_messages

    def add_message_to_chat(self, value):
        self._chat_messages.append(value)

    @property
    def chat_id(self):
        return self._chat_id

    @chat_id.setter
    def chat_id(self, value):
        self._chat_id = value

    @property
    def room(self):
        return self._room

    @room.setter
    def room(self, value):
        self._room = value