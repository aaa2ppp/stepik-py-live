from flask import redirect
from flask.helpers import url_for
from functools import wraps

from session import SessionService


def authorization_required(f):
    """
    Decorate routes to require authorization

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_service = SessionService()
        if session_service.get_session_key():
            return f(*args, **kwargs)
        else:
            session_service.create_new_session_key()
            return redirect(url_for("authorization"))
    return decorated_function
