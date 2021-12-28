from flask import Flask, render_template, request, redirect
from flask.helpers import url_for
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import InputRequired, NumberRange

from game_of_live import GameOfLife



app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Q: What this?
app.config["SECRET_KEY"] = "R2Gl3QGoPnqDth4N"

app.config["WORLD_MIN_SIZE"] = 10
app.config["WORLD_MAX_SIZE"] = 100
app.config["WORLD_DEFAULT_SIZE"] = 20


class WorldSizeForm(FlaskForm):
    __default_height = app.config["WORLD_DEFAULT_SIZE"]
    __default_width = app.config["WORLD_DEFAULT_SIZE"]

    @staticmethod
    def default_height():
        return WorldSizeForm.__default_height

    @staticmethod
    def default_width():
        return WorldSizeForm.__default_width

    height = IntegerField(
        "Высота мира",
        default=default_height,
        validators=[
            InputRequired(),
            NumberRange(app.config["WORLD_MIN_SIZE"], app.config["WORLD_MAX_SIZE"])
        ]
    )
    width = IntegerField(
        "Ширина мира",
        default=default_width,
        validators=[
            InputRequired(),
            NumberRange(app.config["WORLD_MIN_SIZE"], app.config["WORLD_MAX_SIZE"])
        ]
    )
    submit = SubmitField("Принять")

    def validate_on_submit(self):
        result = super().validate_on_submit()
        if result:
            WorldSizeForm.__default_height = self.height.data
            WorldSizeForm.__default_width = self.width.data
        return result

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
def index():
    form = WorldSizeForm()
    if request.method == "POST" and form.validate_on_submit():
        GameOfLife(
            height=form.height.data,
            width=form.width.data
        )
        return redirect("/live")

    else:
        return render_template(url_for("index"), form=form)


@app.route("/live")
def live():
    game = GameOfLife()
    game.form_new_generation()
    return render_template(url_for("live"), game=game)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
