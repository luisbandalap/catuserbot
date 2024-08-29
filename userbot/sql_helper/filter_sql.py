# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# CatUserBot #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Copyright (C) 2020-2023 by TgCatUB@Github.

# This file is part of: https://github.com/TgCatUB/catuserbot
# and is released under the "GNU v3.0 License Agreement".

# Please see: https://github.com/TgCatUB/catuserbot/blob/master/LICENSE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

from contextlib import contextmanager

from sqlalchemy import Column, Numeric, String, UnicodeText
from sqlalchemy.exc import SQLAlchemyError

from . import BASE, SESSION


class Filter(BASE):
    __tablename__ = "catfilters"
    chat_id = Column(String(14), primary_key=True)
    keyword = Column(UnicodeText, primary_key=True, nullable=False)
    reply = Column(UnicodeText)
    f_mesg_id = Column(Numeric)

    def __init__(self, chat_id, keyword, reply, f_mesg_id):
        self.chat_id = str(chat_id)
        self.keyword = keyword
        self.reply = reply
        self.f_mesg_id = f_mesg_id

    def __eq__(self, other):
        return isinstance(other, Filter) and self.chat_id == other.chat_id and self.keyword == other.keyword


Filter.__table__.create(checkfirst=True)


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


def get_filter(chat_id, keyword):
    with session_scope() as session:
        return session.query(Filter).get((str(chat_id), keyword))


def get_filters(chat_id):
    with session_scope() as session:
        return session.query(Filter).filter(Filter.chat_id == str(chat_id)).all()


def add_filter(chat_id, keyword, reply, f_mesg_id):
    with session_scope() as session:
        to_check = session.query(Filter).get((str(chat_id), keyword))
        if not to_check:
            adder = Filter(str(chat_id), keyword, reply, f_mesg_id)
            session.add(adder)
            return True
        session.delete(to_check)
        adder = Filter(str(chat_id), keyword, reply, f_mesg_id)
        session.add(adder)
        return False


def remove_filter(chat_id, keyword):
    with session_scope() as session:
        to_check = session.query(Filter).get((str(chat_id), keyword))
        if not to_check:
            return False
        session.delete(to_check)
        return True


def remove_all_filters(chat_id):
    with session_scope() as session:
        session.query(Filter).filter(Filter.chat_id == str(chat_id)).delete()
