from flask import Flask, render_template, request, redirect, url_for
from forms import WorldSizeForm

from game_of_life import GameOfLife, NoCellGenerationError
from helpers import html_prettify, html_minify, open_session
from util.session import SessionService

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SECRET_KEY"] = b'TIq2mUesnvuk/c9CdnZ/B+4guM+u/PkoKs27NNDxZ8I'

# Tell browser to don't cache anything
# @app.after_request
# def after_request(response):
#     response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     response.headers["Expires"] = 0
#     response.headers["Pragma"] = "no-cache"
#     return response

if app.debug:
    render_template = html_prettify(render_template)
else:
    render_template = html_minify(render_template)


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
    if request.method == "POST" and form.validate_on_submit():
        GameOfLife(context).create_new_life(height=form.height.data, width=form.width.data)
        return redirect(url_for("live", autoUpdate="on"))
    else:
        return render_template("index.html", form=form)


@app.route("/live")
@open_session
def live(context):
    try:
        cells = GameOfLife(context).get_next_generation()
        return render_template("live.html", cells=cells)
    except NoCellGenerationError:
        return no_cell_generation_error_message()


@app.route("/world")
@open_session
def world(context):
    try:
        cells = GameOfLife(context).get_next_generation()
        return render_template("world.html", cells=cells)
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
    GameOfLife(context).create_new_life(20, 20)
    return redirect(url_for("live"))


@app.route("/new-world")
@open_session
def new_world(context):
    GameOfLife(context).create_new_life(20, 20)
    return redirect(url_for("world"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
