from uuid import uuid4
from threading import Lock
from flask import redirect, session
from typing import Optional

from singleton import SingletonMeta


class ErrorAuthorizationRequired(Exception):
    pass


class SessionService(metaclass=SingletonMeta):
    _ss_key = "xG4chG9PdKExwbGmR4"

    def __init__(self):
        self._contexts = {}

    @classmethod
    def get_session_key(cls) -> Optional[str]:
        return session.get(cls._ss_key)

    @classmethod
    def has_session(cls) -> Optional[str]:
        return cls.get_session_key() is not None

    @classmethod
    def create_new_session(cls) -> str:
        key = str(uuid4())
        session[cls._ss_key] = key
        return key

    def get_session_context(self) -> 'SessionContext':
        key = self.get_session_key()
        if key is None:
            raise ErrorAuthorizationRequired("Can't get session key")

        self._lock.acquire()

        session_context = self._contexts.get(key)
        if session_context is None:
            session_context = SessionContext()
            self._contexts[key] = session_context

        self._lock.release()

        return session_context


class SessionContext:
    """
    To obtain an instance of the SessionContext, you SHOULD use the get_session_context method of the
    SessionService object. You MUST always use `with' to ensure thread safety.

    with SessionService().get_session_context() as context:
        # get data from context
        foo = context.data['foo']

        # make some data changes
        ...

        # save data to context
        context.data['foo'] = foo
    """

    def __init__(self):
        self._data = {}
        self._lock = Lock()

    def __enter__(self):
        self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._lock.locked():
            self._lock.release()

    @property
    def data(self) -> dict:
        return self._data

    @property
    def lock(self) -> Lock:
        return self._lock
