from functools import wraps

from flask import request, url_for, redirect, render_template, Response

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
        return tuple(map(int, request.cookies.get("wss").split('x')))
    except (AttributeError, ValueError):
        return 1024, 768


def invalid_parameter_message(param_name: str, err_message: str):
    code = 500
    message = f"Недопустимое значение параметра '{param_name}': {err_message}"
    return render_template("error.html", message=message, code=code), code


def render_plain_world(generation):
    # first two lines
    text = ["".join((str(generation.serial), '\n', "GAME OVER\n" if generation.is_over else "\n"))]

    width = generation.width
    for row in range(generation.height):
        text.append("".join(str(generation.cell_state(row, col).value) for col in range(width)))
        text.append('\n')

    response = Response("".join(text))
    response.headers['Content-Type'] = "text/plain; charset=utf-8"
    return response
