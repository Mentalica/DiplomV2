from typing import List

from user import User


class Room:
    def __init__(self, room_id, owner: User, room_name=None):
        self._room_id = room_id
        self._room_name = room_name
        self._user_list: List[User] = [owner]
        self._owner = owner
        self.add_room_to_user(owner)
        self._chat = None

    def add_room_to_user(self, user: User):
        user.add_room_to_list(self._room_id)

    def add_user_to_room(self, user: User):
        self._user_list.append(user)

    def delete_user_from_room(self):
        pass

    def check_privileges(self):
        pass

    def check_user(self):
        pass

    @property
    def room_id(self):
        return self._room_id

    @room_id.setter
    def room_id(self, value):
        self._room_id = value

    @property
    def room_name(self):
        return self._room_name

    @room_name.setter
    def room_name(self, value):
        self._room_name = value

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, value):
        self._owner = value

    @property
    def chat(self):
        return self._chat

    @chat.setter
    def chat(self, value):
        self._chat = value
