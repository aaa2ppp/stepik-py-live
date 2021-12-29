from flask import Flask, render_template, request, redirect
from flask.helpers import url_for
from game_of_life import GameOfLife
from forms import WorldSizeForm


app = Flask(__name__)

# Ensure templates are auto-reloaded
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
        return redirect(url_for("live"))

    else:
        return render_template("index.html", form=form)


@app.route("/live")
def live():
    game = GameOfLife()
    game.form_new_generation()
    return render_template("live.html", game=game)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
