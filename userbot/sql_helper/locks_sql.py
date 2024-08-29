# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# CatUserBot #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Copyright (C) 2020-2023 by TgCatUB@Github.

# This file is part of: https://github.com/TgCatUB/catuserbot
# and is released under the "GNU v3.0 License Agreement".

# Please see: https://github.com/TgCatUB/catuserbot/blob/master/LICENSE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

from contextlib import contextmanager

from sqlalchemy import Boolean, Column, String
from sqlalchemy.exc import SQLAlchemyError

from . import BASE, SESSION


class Locks(BASE):
    __tablename__ = "locks"
    chat_id = Column(String(14), primary_key=True)
    # Booleans are for "is this locked", _NOT_ "is this allowed"
    bots = Column(Boolean, default=False)
    commands = Column(Boolean, default=False)
    email = Column(Boolean, default=False)
    forward = Column(Boolean, default=False)
    url = Column(Boolean, default=False)

    def __init__(self, chat_id):
        self.chat_id = str(chat_id)  # ensure string
        self.bots = False
        self.commands = False
        self.email = False
        self.forward = False
        self.url = False


Locks.__table__.create(checkfirst=True)


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


def init_locks(chat_id, reset=False):
    with session_scope() as session:
        curr_restr = session.query(Locks).get(str(chat_id))
        if reset and curr_restr:
            session.delete(curr_restr)
            session.flush()
        restr = Locks(str(chat_id))
        session.add(restr)
        return restr


def update_lock(chat_id, lock_type, locked):
    with session_scope() as session:
        curr_perm = session.query(Locks).get(str(chat_id)) or init_locks(chat_id)
        if lock_type == "bots":
            curr_perm.bots = locked
        elif lock_type == "commands":
            curr_perm.commands = locked
        elif lock_type == "email":
            curr_perm.email = locked
        elif lock_type == "forward":
            curr_perm.forward = locked
        elif lock_type == "url":
            curr_perm.url = locked
        session.add(curr_perm)


def is_locked(chat_id, lock_type):
    with session_scope() as session:
        curr_perm = session.query(Locks).get(str(chat_id))
        if not curr_perm:
            return False
        if lock_type == "bots":
            return curr_perm.bots
        if lock_type == "commands":
            return curr_perm.commands
        if lock_type == "email":
            return curr_perm.email
        if lock_type == "forward":
            return curr_perm.forward
        if lock_type == "url":
            return curr_perm.url


def get_locks(chat_id):
    with session_scope() as session:
        return session.query(Locks).get(str(chat_id))
