from uuid import uuid4
from threading import Lock
from flask import redirect, session
from typing import Optional


class SingletonMeta(type):

    def __init__(cls, *args, **kwargs):
        super(SingletonMeta, cls).__init__(*args, **kwargs)
        cls._instance = None
        cls._lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            instance = cls._instance
            if instance is None:
                instance = super(SingletonMeta, cls).__call__(*args, **kwargs)
                cls._instance = instance
        return instance


class ErrorAuthorizationRequired(Exception):
    pass


class SessionService(metaclass=SingletonMeta):
    _ss_key = "ss_key"

    def __init__(self):
        self._contexts = {}

    @classmethod
    def get_session_key(cls) -> Optional[str]:
        return session.get(cls._ss_key)

    @classmethod
    def create_new_session_key(cls) -> str:
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
    External code MUST use `with' for safety use instance of `SessionContext' class in multithreading environment.

    with SessionService().get_session_context() as context:
        # get data for context
        foo = context.data['foo']
        bar = context.data['bar']
        baz = context.data['baz']

        # make some data changes
        ...

        # save data to context
        context.data['foo'] = foo
        context.data['bar'] = bar
        context.data['baz'] = baz
    """

    def __init__(self):
        self._data = {}
        self._lock = Lock()

    @property
    def data(self):
        return self._data

    def __enter__(self):
        self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._lock.release()

