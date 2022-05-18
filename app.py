import os

from flask import Flask, render_template, request, redirect, url_for
from forms import WorldSizeForm

from game_of_life import GameOfLife, NoCellGenerationError
from helpers import html_prettify, html_minify, open_session
from util.session import SessionService

app = Flask(__name__)

app.config["SECRET_KEY"] = b'TIq2mUesnvuk/c9CdnZ/B+4guM+u/PkoKs27NNDxZ8I'
if app.debug:
    app.config["TEMPLATES_AUTO_RELOAD"] = True

app.jinja_options["trim_blocks"] = True
app.jinja_options["lstrip_blocks"] = True
app.jinja_options["keep_trailing_newline"] = True

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
        code = 403
        title = "Create session error"
        message = "Can't create session. This usually happens if your browser blocks cookies."
        return render_template("error.html", title=title, message=message, code=code), code


@app.route("/", methods=["GET", "POST"])
@open_session
def index(context):
    form = WorldSizeForm(context)
    if form.validate_on_submit():
        GameOfLife(context).create_new_life(height=form.height.data, width=form.width.data)
        context.data['disable_js'] = form.disable_js.data
        if context.data['disable_js']:
            return redirect(url_for("live"))
        else:
            return redirect(url_for("live", autoupdate="on", update_period=form.update_period.data))
    else:
        return render_template("index.html", form=form)


@app.route("/live")
@open_session
def live(context):
    try:
        game = GameOfLife(context)
        cells = game.get_next_generation()
        return render_template("live.html", cells=cells, game_over=game.is_over(), disable_js=context.get('disable_js'))
    except NoCellGenerationError:
        return no_cell_generation_error_message()


@app.route("/world")
@open_session
def world(context):
    try:
        game = GameOfLife(context)
        cells = game.get_next_generation()
        return render_template("world.html", cells=cells, game_over=game.is_over())
    except NoCellGenerationError:
        return no_cell_generation_error_message()


def no_cell_generation_error_message():
    code = 500
    message = ("I'm sorry, but there was an error. There is no generation of cells." +
               " Please create new life.")
    return render_template("error.html", message=message, code=code), code


# The following two direct links are FOR TESTS ONLY

@app.route("/new-live")
@open_session
def new_live(context):
    GameOfLife(context).create_new_life(25, 25)
    context.data['disable_js'] = True
    return redirect(url_for("live"))


@app.route("/new-world")
@open_session
def new_world(context):
    GameOfLife(context).create_new_life(25, 25)
    context.data['disable_js'] = True
    return redirect(url_for("world"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
