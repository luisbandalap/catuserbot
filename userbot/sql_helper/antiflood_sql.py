# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# CatUserBot #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Copyright (C) 2020-2023 by TgCatUB@Github.

# This file is part of: https://github.com/TgCatUB/catuserbot
# and is released under the "GNU v3.0 License Agreement".

# Please see: https://github.com/TgCatUB/catuserbot/blob/master/LICENSE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

import threading
from contextlib import contextmanager

from sqlalchemy import Column, Integer, String
from sqlalchemy.exc import SQLAlchemyError

from . import BASE, SESSION

DEF_COUNT = 0
DEF_LIMIT = 0
DEF_OBJ = (None, DEF_COUNT, DEF_LIMIT)


class FloodControl(BASE):
    __tablename__ = "antiflood"
    chat_id = Column(String(14), primary_key=True)
    user_id = Column(Integer)
    count = Column(Integer, default=DEF_COUNT)
    limit = Column(Integer, default=DEF_LIMIT)

    def __init__(self, chat_id):
        self.chat_id = str(chat_id)  # ensure string

    def __repr__(self):
        return f"<flood control for {self.chat_id}>"


FloodControl.__table__.create(checkfirst=True)

INSERTION_LOCK = threading.RLock()


class ANTIFLOOD_SQL:
    def __init__(self):
        self.CHAT_FLOOD = {}


ANTIFLOOD_SQL_ = ANTIFLOOD_SQL()


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = SESSION()
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise e
    finally:
        session.close()


def set_flood(chat_id, amount):
    with INSERTION_LOCK, session_scope() as session:
        flood = session.query(FloodControl).get(str(chat_id)) or FloodControl(str(chat_id))

        flood.user_id = None
        flood.limit = amount

        ANTIFLOOD_SQL_.CHAT_FLOOD[str(chat_id)] = (None, DEF_COUNT, amount)

        session.add(flood)


def update_flood(chat_id: str, user_id) -> bool:
    with INSERTION_LOCK:
        if chat_id not in ANTIFLOOD_SQL_.CHAT_FLOOD:
            return False
        curr_user_id, count, limit = ANTIFLOOD_SQL_.CHAT_FLOOD.get(chat_id, DEF_OBJ)
        if limit == 0:  # no antiflood
            return False
        if user_id != curr_user_id or user_id is None:  # other user
            ANTIFLOOD_SQL_.CHAT_FLOOD[chat_id] = (user_id, DEF_COUNT + 1, limit)
            return False

        count += 1
        if count > limit:  # too many msgs, kick
            ANTIFLOOD_SQL_.CHAT_FLOOD[chat_id] = (None, DEF_COUNT, limit)
            return True

        # default -> update
        ANTIFLOOD_SQL_.CHAT_FLOOD[chat_id] = (user_id, count, limit)
        return False


def get_flood_limit(chat_id):
    return ANTIFLOOD_SQL_.CHAT_FLOOD.get(str(chat_id), DEF_OBJ)[2]


def migrate_chat(old_chat_id, new_chat_id):
    with INSERTION_LOCK, session_scope() as session:
        if flood := session.query(FloodControl).get(str(old_chat_id)):
            ANTIFLOOD_SQL_.CHAT_FLOOD[str(new_chat_id)] = ANTIFLOOD_SQL_.CHAT_FLOOD.get(str(old_chat_id), DEF_OBJ)
            flood.chat_id = str(new_chat_id)


def __load_flood_settings():
    with session_scope() as session:
        all_chats = session.query(FloodControl).all()
        ANTIFLOOD_SQL_.CHAT_FLOOD = {chat.chat_id: (None, DEF_COUNT, chat.limit) for chat in all_chats}
    return ANTIFLOOD_SQL_.CHAT_FLOOD
