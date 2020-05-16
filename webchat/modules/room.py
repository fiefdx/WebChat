# -*- coding: UTF-8 -*-

import json
import time
import logging

LOG = logging.getLogger("__name__")


class Room(object):
    def __init__(self, room_id):
        self.room_id = room_id
        self.current_members = 0
        self.connections = []

    def add(self, conn):
        self.connections.append(conn)
        self.current_members += 1

    def remove(self, conn):
        self.connections.remove(conn)
        self.current_members -= 1

    def broadcast(self, msg):
        try:
            encrypt = ""
            if "encrypt" in msg:
                encrypt = msg["encrypt"]
                msg["encrypt"] = ""
            dead_connections = []
            for conn in self.connections:
                try:
                    if "encrypt" in msg:
                        msg["msg"] = conn.encrypt_msg(encrypt)
                    conn.write_message(msg)
                except Exception as e:
                    LOG.exception(e)
                    dead_connections.append(conn)
            for conn in dead_connections:
                conn.close()
                self.connections.remove(conn)
        except Exception as e:
            LOG.exception(e)


class Rooms(object):
    def __init__(self, room_num = 100):
        self.rooms = {}
        for i in range(room_num + 1):
            self.rooms[i] = Room(i)

    def __getitem__(self, room_id):
        return self.rooms[room_id]
