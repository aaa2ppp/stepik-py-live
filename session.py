from threading import Lock
from typing import Dict

import flask


class ServerSideSession:
    _lock = Lock()
    _flask_session_key = 'ee189389-a72c-4225-a44e-e7c02f7ae222'
    _data = {}

    @classmethod
    def lock(cls) -> Lock:
        return cls._lock

    @classmethod
    def get_session_date(cls) -> Dict:
        key = flask.session.get(cls._flask_session_key)
        data = cls._data.get(key)
        if data is None:
            data = {}
            cls._data[key] = data
        return cls._data


def server_session(func):
    def _wrapper(*args, **kwargs):
        with ServerSideSession.lock():
            session_data = ServerSideSession.get_session_date()
            func(*args, **kwargs)

    return _wrapper()
