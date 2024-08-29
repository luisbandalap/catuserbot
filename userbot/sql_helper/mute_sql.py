# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# CatUserBot #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Copyright (C) 2020-2023 by TgCatUB@Github.

# This file is part of: https://github.com/TgCatUB/catuserbot
# and is released under the "GNU v3.0 License Agreement".

# Please see: https://github.com/TgCatUB/catuserbot/blob/master/LICENSE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

from contextlib import contextmanager

from sqlalchemy import Column, String
from sqlalchemy.exc import SQLAlchemyError

from . import BASE, SESSION


class Mute(BASE):
    __tablename__ = "mute"
    sender = Column(String(14), primary_key=True)
    chat_id = Column(String(14), primary_key=True)

    def __init__(self, sender, chat_id):
        self.sender = str(sender)
        self.chat_id = str(chat_id)


Mute.__table__.create(checkfirst=True)


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


def is_muted(sender, chat_id):
    with session_scope() as session:
        user = session.query(Mute).get((str(sender), str(chat_id)))
        return bool(user)


def mute(sender, chat_id):
    with session_scope() as session:
        adder = Mute(str(sender), str(chat_id))
        session.add(adder)


def unmute(sender, chat_id):
    with session_scope() as session:
        if rem := session.query(Mute).get((str(sender), str(chat_id))):
            session.delete(rem)
