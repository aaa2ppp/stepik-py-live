from functools import wraps

from flask import request, url_for, redirect

from util.session import SessionService


def open_session(f):
    """
    Decorator to create session and giving the session context to wrapped function.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_service = SessionService()
        if session_service.has_session():
            with session_service.get_session_context() as context:
                return f(context, *args, **kwargs)
        else:
            session_service.create_session()
            return redirect(url_for("check_session", next=request.url))

    return decorated_function


def get_window_screen_size():
    try:
        window_screen_size = tuple(map(int, request.cookies.get("wss", "1024x768").split('x')))
    except:
        window_screen_size = (1024, 640)

    return window_screen_size
