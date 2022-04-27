from wtforms import IntegerField, SubmitField
from wtforms.validators import InputRequired, NumberRange
from flask_wtf import FlaskForm

WORLD_MIN_SIZE = 2
WORLD_MAX_SIZE = 100
WORLD_DEFAULT_SIZE = 20


class WorldSizeForm(FlaskForm):
    # TODO: We can't store it here. This is data must be linked to the session.
    _default_height = WORLD_DEFAULT_SIZE
    _default_width = WORLD_DEFAULT_SIZE

    @staticmethod
    def default_height():
        return WorldSizeForm._default_height

    @staticmethod
    def default_width():
        return WorldSizeForm._default_width

    height = IntegerField(
        "Высота мира",
        default=default_height,
        validators=[
            InputRequired(),
            NumberRange(WORLD_MIN_SIZE, WORLD_MAX_SIZE)
        ]
    )

    width = IntegerField(
        "Ширина мира",
        default=default_width,
        validators=[
            InputRequired(),
            NumberRange(WORLD_MIN_SIZE, WORLD_MAX_SIZE)
        ]
    )

    submit = SubmitField("Создать жизнь")

    def validate_on_submit(self):
        result = super().validate_on_submit()
        if result:
            # TODO: see above
            WorldSizeForm._default_height = self.height.data
            WorldSizeForm._default_width = self.width.data
        return result
