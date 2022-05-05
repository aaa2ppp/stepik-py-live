from uuid import uuid4
from threading import Lock
from flask import session as flask_session
from typing import Optional

from util.singleton import SingletonMeta


class SessionContentError(Exception):
    pass


class CanNotGetSessionKeyError(Exception):
    pass


class SessionService(metaclass=SingletonMeta):
    _fss_key = "xG4chG9PdKExwbGmR4"

    def __init__(self):
        self._contexts = {}

    @classmethod
    def _get_session_key(cls) -> Optional[str]:
        return flask_session.get(cls._fss_key)

    @classmethod
    def _create_session_key(cls) -> str:
        key = str(uuid4())
        flask_session[cls._fss_key] = key
        return key

    def has_session(self):
        return self._get_session_key() is not None

    def create_session(self):
        self._create_session_key()

    def get_session_context(self) -> 'SessionContext':
        key = self._get_session_key()
        if key is None:
            raise SessionContentError("Can't get session key")

        with self._lock:
            context = self._contexts.get(key)
            if context is None:
                self._contexts[key] = context = SessionContext()

        return context


class SessionContext:
    """
    To obtain an instance of the `SessionContext`, you SHOULD use the `get_session_context` method of the
    `SessionService` object. You MUST always use `with` to ensure thread safety.

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
        self._lock.release()

    @property
    def data(self) -> dict:
        return self._data

    def get(self, key):
        return self._data.get(key)

    def get_dict(self, key) -> dict:
        data = self._data.get(key)
        if data is None:
            self._data[key] = data = {}
        return data

    def get_list(self, key) -> list:
        data = self._data.get(key)
        if data is None:
            self._data[key] = data = []
        return data
