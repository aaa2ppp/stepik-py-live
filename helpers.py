from flask import redirect, request
from flask.helpers import url_for
from functools import wraps

from session import SessionService


# def login_required(f):
#     """
#     Decorate routes to require login.
#
#     http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
#     """
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if session.get("user_id") is None:
#             return redirect("/login")
#         return f(*args, **kwargs)
#     return decorated_function


def open_session(f):
    """
    Decorator to open session and giving the session context data to wrapped function.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_service = SessionService()
        if session_service.has_session():
            with session_service.get_session_context() as context:
                return f(context.data, *args, **kwargs)
        else:
            session_service.create_new_session()
            return redirect(url_for("check_session", next=request.url))

    return decorated_function
