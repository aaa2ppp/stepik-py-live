from wtforms import IntegerField, SubmitField
from wtforms.validators import InputRequired, NumberRange
from flask_wtf import FlaskForm

WORLD_MIN_SIZE = 3
WORLD_MAX_SIZE = 100
WORLD_DEFAULT_SIZE = 20


class WorldSizeForm(FlaskForm):
    # TODO: we should use successful input as future defaults

    @property
    def min_size(self):
        return WORLD_MIN_SIZE

    @property
    def max_size(self):
        return WORLD_MAX_SIZE

    def __init__(self, context_data: dict):
        super().__init__()
        self._context_data = context_data.setdefault(self.__class__, {})

    def validate_on_submit(self):
        result = super().validate_on_submit()

        if result:
            self._context_data['default_height'] = self.height.data
            self._context_data['default_width'] = self.width.data

        return result

    height = IntegerField(
        "Высота мира",
        default=WORLD_DEFAULT_SIZE,
        validators=[
            InputRequired(),
            NumberRange(WORLD_MIN_SIZE, WORLD_MAX_SIZE)
        ]
    )

    width = IntegerField(
        "Ширина мира",
        default=WORLD_DEFAULT_SIZE,
        validators=[
            InputRequired(),
            NumberRange(WORLD_MIN_SIZE, WORLD_MAX_SIZE)
        ]
    )

    submit = SubmitField("Создать жизнь")

