from flask import Flask, render_template, request, redirect
from flask.helpers import url_for
from game_of_life import GameOfLife
from forms import WorldSizeForm

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SECRET_KEY"] = b'TIq2mUesnvuk/c9CdnZ/B+4guM+u/PkoKs27NNDxZ8I'


@app.route("/", methods=["GET", "POST"])
def index():
    form = WorldSizeForm()
    if request.method == "POST" and form.validate_on_submit():
        with GameOfLife() as game:
            game.create_new_life(height=form.height.data, width=form.width.data)
        return redirect(url_for("live", autoUpdate="on"))
    else:
        return render_template("index.html", form=form)


@app.route("/live")
def live():
    with GameOfLife() as game:
        return render_template("live.html", cells=game.get_next_generation())


@app.route("/world")
def world():
    with GameOfLife() as game:
        return render_template("world.html", cells=game.get_next_generation())


# The following two direct links are FOR TESTS ONLY

@app.route("/new-live")
def new_live():
    with GameOfLife() as game:
        game.create_new_life()
    return redirect(url_for("live"))


@app.route("/new-world")
def new_world():
    with GameOfLife() as game:
        game.create_new_life()
    return redirect(url_for("world"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
