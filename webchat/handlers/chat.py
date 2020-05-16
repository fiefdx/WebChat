# -*- coding: utf-8 -*-

import json
import time
import logging
from uuid import uuid4
import base64
import datetime

from tornado import web
from tornado import gen

from webchat.handlers.base import BaseHandler, BaseSocketHandler
from webchat.modules.room import Rooms
from webchat.utils.pytea import str_encrypt, str_decrypt
from webchat.utils.common import md5twice
from webchat.config import CONFIG

LOG = logging.getLogger("__name__")


class ChatHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        self.render(
            "chat/chat.html",
            current_nav = "Chat",
            scheme = "http",
            locale = "en_US"
        )


class ChatSocketHandler(BaseSocketHandler):
    guest_prefix = "Guest_"
    room_num = 100
    rooms = Rooms(100)
    connection_id_counter = 0

    @gen.coroutine
    def open(self, room_id):
        self.nickname = "%s%s" % (ChatSocketHandler.guest_prefix, self.get_id())
        self.room_id = int(room_id)
        self.password = uuid4()
        ChatSocketHandler.rooms[self.room_id].add(self)
        message = "* %s joined" % (self.nickname)
        data = {}
        data["cmd"] = "init_rooms_list"
        data["msg"] = base64.b64encode(message.encode("utf-8")).decode("utf-8")
        data["password"] = self.password.hex
        data["rooms_list"] = []
        for i in range(1, ChatSocketHandler.room_num + 1):
            data["rooms_list"].append({
                "room_id": ChatSocketHandler.rooms[i].room_id,
                "current_members": ChatSocketHandler.rooms[i].current_members,
            })
        data["default_nick_name"] = base64.b64encode(self.nickname.encode("utf-8")).decode("utf-8")
        self.write_message(data)

    @gen.coroutine
    def on_message(self, msg):
        now = datetime.datetime.now()
        msg = json.loads(msg)
        cmd = msg["cmd"]
        if cmd == "change_room":
            room_id = int(msg["room_id"])
            if room_id != 0:
                data = {}
                ChatSocketHandler.rooms[self.room_id].remove(self)
                data["cmd"] = "new_msg"
                message = "System (%s) : %s left." % (now.strftime("%Y-%m-%d %H:%M:%S"), self.nickname)
                data["msg"] = base64.b64encode(message.encode("utf-8")).decode("utf-8")
                ChatSocketHandler.rooms[self.room_id].broadcast(data)

                data = {}
                self.room_id = room_id
                ChatSocketHandler.rooms[self.room_id].add(self)
                data["cmd"] = "new_msg"
                message = "System (%s) : %s joined." % (now.strftime("%Y-%m-%d %H:%M:%S"), self.nickname)
                data["msg"] = base64.b64encode(message.encode("utf-8")).decode("utf-8")
                ChatSocketHandler.rooms[self.room_id].broadcast(data)
            else:
                data = {}
                self.room_id = room_id
                ChatSocketHandler.rooms[self.room_id].add(self)
                data["cmd"] = "new_msg"
                message = "System (%s) : %s joined." % (now.strftime("%Y-%m-%d %H:%M:%S"), self.nickname)
                data["msg"] = base64.b64encode(message.encode("utf-8")).decode("utf-8")
                ChatSocketHandler.rooms[self.room_id].broadcast(data)

            data = {}
            data["cmd"] = "change_rooms_list"
            data["rooms_list"] = []
            data_refresh = {}
            data_refresh["cmd"] = "refresh_rooms_list"
            data_refresh["rooms_list"] = []
            for i in range(1, ChatSocketHandler.room_num + 1):
                room_info = {
                    "room_id": ChatSocketHandler.rooms[i].room_id,
                    "current_members": ChatSocketHandler.rooms[i].current_members,
                }
                data["rooms_list"].append(room_info)
                data_refresh["rooms_list"].append(room_info)
            self.broadcast_all(data_refresh)

            data["room_id"] = self.room_id
            data["nick_name"] = base64.b64encode(self.nickname.encode("utf-8")).decode("utf-8")
            self.write_message(data)
        elif cmd == "send_msg":
            room_id = int(msg["room_id"])
            nickname_base64 = msg["nick_name"]
            default_name_base64 = msg["default_nick_name"]
            msg_base64 = msg["msg"]

            msg_string = self.decrypt_msg(msg_base64)

            data = {}
            if room_id != 0:
                data["cmd"] = "new_msg"
                data["date_time"] = now.strftime("%Y-%m-%d %H:%M:%S")
                data["nick_name"] = nickname_base64
                data["default_nick_name"] = default_name_base64
                data["encrypt"] = msg_string
                data["msg"] = msg_string
                ChatSocketHandler.rooms[room_id].broadcast(data)

    @gen.coroutine
    def on_close(self):
        now = datetime.datetime.now()
        ChatSocketHandler.rooms[self.room_id].remove(self)

        data = {}
        data["cmd"] = "new_msg"
        message = "System (%s) : %s left." % (now.strftime("%Y-%m-%d %H:%M:%S"), self.nickname)
        data["msg"] = base64.b64encode(message.encode("utf-8")).decode("utf-8")
        ChatSocketHandler.rooms[self.room_id].broadcast(data)

        data = {}
        data["cmd"] = "refresh_rooms_list"
        data["rooms_list"] = []
        for i in range(1, ChatSocketHandler.room_num + 1):
            room_info = {
                "room_id": ChatSocketHandler.rooms[i].room_id,
                "current_members": ChatSocketHandler.rooms[i].current_members,
            }
            data["rooms_list"].append(room_info)
        self.broadcast_all(data)
        self.close()
        LOG.info("close websocket")

    def get_id(self):
        ChatSocketHandler.connection_id_counter += 1
        return ChatSocketHandler.connection_id_counter

    def broadcast_all(self, msg):
        for i in range(ChatSocketHandler.room_num + 1):
            ChatSocketHandler.rooms[i].broadcast(msg)

    def encrypt_msg(self, msg):
        key = md5twice(self.password.hex)
        result_string = str_encrypt(msg, key)
        return base64.b64encode(result_string).decode("utf-8")

    def decrypt_msg(self, msg):
        key = md5twice(self.password.hex)
        msg_bytes = base64.b64decode(msg)
        result_string = str_decrypt(msg_bytes, key)
        return result_string
