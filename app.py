import os

from flask import Flask, render_template, request, redirect, url_for
from forms import WorldSizeForm

from game_of_life import GameOfLife, NoGenerationError
from helpers import open_session, get_window_screen_size, invalid_parameter_message
from util.session import SessionService

app = Flask(__name__)

app.config["SECRET_KEY"] = b'TIq2mUesnvuk/c9CdnZ/B+4guM+u/PkoKs27NNDxZ8I'
if app.debug:
    app.config["TEMPLATES_AUTO_RELOAD"] = True

app.jinja_options["trim_blocks"] = True
app.jinja_options["lstrip_blocks"] = True
app.jinja_options["keep_trailing_newline"] = False

# Tell browser to don't cache anything
if int(os.environ.get('NO_CACHE', "0")):
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response


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
        GameOfLife(context).create_new_life(height=form.height.data, width=form.width.data)
        if form.js_off.data:
            return redirect(url_for("live",
                                    js="off",
                                    serial=form.serial.data))
        else:
            return redirect(url_for("live",
                                    js="on",
                                    autoupdate=form.autoupdate.data,
                                    update_period=form.update_period.data,
                                    serial=form.serial.data))
    else:
        return render_template("index.html", form=form)


@app.route("/live")
@open_session
def live(context):
    js = request.args.get('js')
    if js is not None and js in ("no", "off", "false", "0"):
        js = False
    else:
        js = True
    return render_live(context, "live.html", js=js)


@app.route("/world")
@open_session
def world(context):
    return render_live(context, "world.html")


def render_live(context, template: str, **kwargs):
    serial = request.args.get('serial')
    if serial is not None:
        try:
            serial = int(serial)
        except ValueError:
            return invalid_parameter_message("serial", "Должно быть целое число")

        if serial < 0:
            return invalid_parameter_message("serial", "Должно быть больше 0")

    try:
        game = GameOfLife(context)
        generation = game.get_next_generation() if serial is None else game.get_generation(serial)
    except NoGenerationError:
        code = 500
        message = "Нет ни одного поколения клеток. Пожалуйста создайте новую жизнь."
        return render_template("error.html", message=message, code=code), code

    wss = get_window_screen_size()
    return render_template(template, generation=generation, wss=wss, **kwargs)


@app.route("/nothing_works")
def nothing_works():
    return render_template("message-for-reviewers.html")


# The following two direct links are FOR TESTS ONLY

@app.route("/new_live")
@open_session
def new_live(context):
    GameOfLife(context).create_new_life(25, 25)
    return redirect(url_for("live", **request.args))


@app.route("/new_world")
@open_session
def new_world(context):
    GameOfLife(context).create_new_life(25, 25)
    return redirect(url_for("world"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
