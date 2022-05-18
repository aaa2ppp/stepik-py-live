from wtforms import IntegerField, SubmitField, BooleanField, SelectField
from wtforms.validators import InputRequired, NumberRange
from flask_wtf import FlaskForm

from util.session import SessionService, SessionContext

_WORLD_MIN_SIZE = 1
_WORLD_MAX_SIZE = 100
_WORLD_DEFAULT_SIZE = 25


class WorldSizeForm(FlaskForm):
    def __init__(self, context: SessionContext):
        super().__init__()
        self._context_data = context.get_dict(self.__class__)

    height = IntegerField(
        "Высота мира",
        default=lambda: _get_default_value('height', _WORLD_DEFAULT_SIZE),
        validators=[
            InputRequired(),
            NumberRange(_WORLD_MIN_SIZE, _WORLD_MAX_SIZE)
        ]
    )

    width = IntegerField(
        "Ширина мира",
        default=lambda: _get_default_value('width', _WORLD_DEFAULT_SIZE),
        validators=[
            InputRequired(),
            NumberRange(_WORLD_MIN_SIZE, _WORLD_MAX_SIZE)
        ]
    )

    update_period = SelectField(
        "Период обновления",
        choices=((2000, "2 сек"), (1000, "1 сек"), (750, "0.75 сек"), (500, "0.5 сек"), (250, "0.25 сек")),
        coerce=int,
        default=lambda: _get_default_value('update_period', 1000)
    )

    disable_js = BooleanField(
        "Не загружать js скрипты",
        default=lambda: _get_default_value('disable_js', False)
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
            self._context_data['height'] = self.height.data
            self._context_data['width'] = self.width.data
            self._context_data['update_period'] = self.update_period.data
            self._context_data['disable_js'] = self.disable_js.data
        return result


def _get_default_value(name: str, default):
    # TODO: It's very expensive. This is a workaround. But so far I don't understand how to pass
    #  the session context data to the form fields in the initiator of the form object.
    context_data = SessionService().get_session_context().get_dict(WorldSizeForm)
    return context_data.get(name, default)
