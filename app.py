import os
import time

from flask import Flask, render_template, request, redirect, url_for
from forms import WorldSizeForm

from game_of_life import GameOfLife, NoGenerationError
from helpers import open_session, get_window_screen_size, invalid_parameter_message, render_plain_world
from util.session import SessionService

app = Flask(__name__)

app.config["SECRET_KEY"] = b'TIq2mUesnvuk/c9CdnZ/B+4guM+u/PkoKs27NNDxZ8I'
if app.debug:
    app.config["TEMPLATES_AUTO_RELOAD"] = True

app.jinja_options["trim_blocks"] = True
app.jinja_options["lstrip_blocks"] = True
app.jinja_options["keep_trailing_newline"] = True

# Tell browser to don't cache anything
if int(os.environ.get('NO_CACHE', '0')):
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

_GAME_VIEWS = ('live', 'world', 'plain_world')


@app.route("/check-session")
def check_session():
    if SessionService().has_session():
        return redirect(request.args.get('next', url_for("index")))
    else:
        code = 401
        title = "Ошибка создания сессии"
        message = ("Я не могу создать сессию. Такое может происходит, если запрещены куки." +
                   f" Пожалуйста, проверьте, что в вашем браузере разрешены куки для {request.host_url[:-1]}.")

        return render_template("error.html", title=title, message=message, code=code), code


@app.route("/", methods=("GET", "POST"))
@open_session
def index(context):
    form = WorldSizeForm(context)

    if form.validate_on_submit():
        GameOfLife(context).create_new_random_life(width=form.width.data, height=form.height.data)

        if form.js_off.data:
            return redirect(url_for("live",
                                    js="off",
                                    serial=form.serial.data))
        else:
            return redirect(url_for("live",
                                    autoupdate=("off", "on")[form.autoupdate.data],
                                    update_period=form.update_period.data,
                                    serial=form.serial.data))

    return render_template("index.html", form=form)


# Direct route to create a new life
@app.route("/new_live")
@app.route("/new_live_<int:width>x<int:height>")
@open_session
def new_live(context, width=None, height=None):
    if width is None:
        width = int(request.args.get('width', 25))

    if height is None:
        height = int(request.args.get('height', 25))

    if width < 1 or height < 1:
        code = 400
        message = "Минимальный допустимый размер поля игры 1х1"
        return render_template("error.html", message=message, code=code), code

    GameOfLife(context).create_new_random_life(width=width, height=height)

    args = dict((k, v) for k, v in request.args.items() if k not in ('width', 'height'))
    return redirect(url_for("live", **args))


@app.route("/live")
@app.route("/<view>")
@open_session
def live(context, view=None):
    if view is None:
        view = request.args.get('view', 'live')

    if view not in _GAME_VIEWS:
        code = 404
        message = f"Страница {request.url} не найдена"
        return render_template("error.html", message=message, code=code), code

    js = request.args.get('js')
    if js is not None and js.lower() in ("no", "off", "false", "0"):
        js = False
    else:
        js = True

    try:
        serial = int(request.args.get('serial', '0'))
    except ValueError:
        return invalid_parameter_message("serial", "Значение должно быть целым числом")
    if serial < 0:
        return invalid_parameter_message("serial", "Значение должно быть больше или равно 0")

    try:
        game = GameOfLife(context)
        generation = game.get_generation(serial)
    except NoGenerationError:
        code = 500
        message = "Нет ни одного поколения клеток. Пожалуйста создайте новую жизнь."
        return render_template("error.html", message=message, code=code), code

    if view == "plain_world":
        # Here the use of "jinja" is not optimal. It will be long and difficult.
        return render_plain_world(generation)
    else:
        wss = get_window_screen_size()
        template = f"{view}.html"
        return render_template(template, generation=generation, js=js, wss=wss)


@app.route("/nothing_works")
def nothing_works():
    return render_template("message-for-reviewers.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
