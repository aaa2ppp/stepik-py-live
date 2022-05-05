import bs4
import htmlmin
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


def html_prettify(f):
    """
    https://stackoverflow.com/questions/13587531/minify-html-output-from-flask-application-with-jinja2-templates
    """

    @wraps(f)
    def wrapped(*args, **kwargs):
        soup = bs4.BeautifulSoup(f(*args, **kwargs), 'html.parser')
        return soup.prettify()

    return wrapped


def html_minify(f):
    """
    https://stackoverflow.com/questions/13587531/minify-html-output-from-flask-application-with-jinja2-templates
    """

    @wraps(f)
    def wrapped(*args, **kwargs):
        return htmlmin.minify(f(*args, **kwargs), remove_empty_space=True, remove_comments=True)

    return wrapped
