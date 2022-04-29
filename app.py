from flask import Flask, render_template, request, redirect
from flask.helpers import url_for
from game_of_life import GameOfLife
from forms import WorldSizeForm

from session import SessionService
from helpers import authorization_required

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SECRET_KEY"] = b'TIq2mUesnvuk/c9CdnZ/B+4guM+u/PkoKs27NNDxZ8I'


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/authorization")
def authorization():
    server_side_session = SessionService()
    if server_side_session.get_session_key() is not None:
        return redirect(url_for("index"))
    else:
        code = 403
        return render_template("error.html", code=code,
                               message="Can't create session. Your browser may be blocking cookies."), code


@app.route("/", methods=["GET", "POST"])
@authorization_required
def index():
    with SessionService().get_session_context() as context:
        form = WorldSizeForm(context.data)
        if request.method == "POST" and form.validate_on_submit():
            GameOfLife().create_new_life(height=form.height.data, width=form.width.data)
            return redirect(url_for("live", autoUpdate="on"))
        else:
            return render_template("index.html", form=form)


@app.route("/live")
@authorization_required
def live():
    with SessionService().get_session_context():
        cells = GameOfLife().get_next_generation()
        return render_template("live.html", cells=cells)


@app.route("/world")
@authorization_required
def world():
    with SessionService().get_session_context():
        cells = GameOfLife().get_next_generation()
        return render_template("world.html", cells=cells)


# The following two direct links are FOR TESTS ONLY

@app.route("/new-live")
@authorization_required
def new_live():
    with SessionService().get_session_context():
        GameOfLife().create_new_life()
    return redirect(url_for("live"))


@app.route("/new-world")
@authorization_required
def new_world():
    with SessionService().get_session_context():
        GameOfLife().create_new_life()
    return redirect(url_for("world"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
