from typing import List

# from user import User


class Room:
    def __init__(self, room_id, owner, room_name=None):
        self._room_id = room_id
        self._room_name = room_name
        self._user_list = [owner]
        # self._user_list: List[User] = [owner]
        self._owner = owner
        self.add_room_to_user(owner)
        self._chat = None

    def add_room_to_user(self, user):
        user.add_room_to_list(self)

    def add_user_to_room(self, user):
        self._user_list.append(user)

    def delete_user_from_room(self, user):
        # self._user_list = [u for u in self._user_list if u != user]
        for user_i in self._user_list:
            if user_i == user:
                self._user_list.remove(user)
                break

    def delete_room_for_users(self):
        for user in self._user_list:
            user.delete_room(self)
            if user.active_room == self:
                user.active_room = None


    def check_user(self, user):
        print("check_user")
        print(self._user_list)
        for user_i in self._user_list:
            print(f"User-i id {user_i.user_id}")
            print(f"User id {user.user_id}")
            if user_i.user_id == user.user_id:
                print(f"user - {user_i.user_id}, user {user.user_id}")
                return True
        return False

    def is_owner(self, user):
        if user == self._owner:
            return True
        else:
            return False

    def get_user_list(self):
        return self._user_list

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
