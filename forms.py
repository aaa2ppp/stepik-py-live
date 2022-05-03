from wtforms import IntegerField, SubmitField
from wtforms.validators import InputRequired, NumberRange
from flask_wtf import FlaskForm

from session import SessionService, SessionContext

_WORLD_MIN_SIZE = 1
_WORLD_MAX_SIZE = 100
_WORLD_DEFAULT_SIZE = 20


class WorldSizeForm(FlaskForm):
    def __init__(self, context: SessionContext):
        super().__init__()
        self._context_data = context.get_dict(self.__class__)

    height = IntegerField(
        "Высота мира",
        default=lambda: _get_default_value('default_height', _WORLD_DEFAULT_SIZE),
        validators=[
            InputRequired(),
            NumberRange(_WORLD_MIN_SIZE, _WORLD_MAX_SIZE)
        ]
    )

    width = IntegerField(
        "Ширина мира",
        default=lambda: _get_default_value('default_width', _WORLD_DEFAULT_SIZE),
        validators=[
            InputRequired(),
            NumberRange(_WORLD_MIN_SIZE, _WORLD_MAX_SIZE)
        ]
    )

    submit = SubmitField("Создать жизнь")

    @property
    def min_size(self):
        return _WORLD_MIN_SIZE

    @property
    def max_size(self):
        return _WORLD_MAX_SIZE

    def validate_on_submit(self):
        result = super().validate_on_submit()
        if result:
            self._context_data['default_height'] = self.height.data
            self._context_data['default_width'] = self.width.data
        return result


def _get_default_value(name: str, default):
    # TODO: It's very expensive. This is a workaround. But so far I don't understand how to pass
    #  the session context data to the form fields in the initiator of the form object.
    context_data = SessionService().get_session_context().get_dict(WorldSizeForm)
    return context_data.get(name, default)
