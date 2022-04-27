from flask import Flask, render_template, request, redirect
from flask.helpers import url_for
from game_of_life import GameOfLife
from forms import WorldSizeForm

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SECRET_KEY"] = "R2Gl3QGoPnqDth4N"


@app.route("/", methods=["GET", "POST"])
def index():
    form = WorldSizeForm()

    if request.method == "POST" and form.validate_on_submit():
        GameOfLife(
            height=form.height.data,
            width=form.width.data
        )
        return redirect(url_for("live", autoUpdate="on"))

    else:
        return render_template("index.html", form=form)


@app.route("/live")
def live():
    game = GameOfLife()
    game.form_new_generation()
    return render_template("live.html", game=game)


@app.route("/world")
def world():
    game = GameOfLife()
    game.form_new_generation()
    return render_template("world.html", game=game)


# The following two direct links are FOR TESTS ONLY

@app.route("/new-live")
def new_live():
    GameOfLife(height=20, width=20)
    return redirect(url_for("live"))


@app.route("/new-world")
def new_world():
    GameOfLife(height=20, width=20)
    return redirect(url_for("world"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
