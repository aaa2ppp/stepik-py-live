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

    height = IntegerField("Высота мира",
                          default=lambda: _get_default_value('height', _WORLD_DEFAULT_SIZE),
                          validators=[InputRequired(),
                                      NumberRange(_WORLD_MIN_SIZE, _WORLD_MAX_SIZE)])

    width = IntegerField("Ширина мира",
                         default=lambda: _get_default_value('width', _WORLD_DEFAULT_SIZE),
                         validators=[InputRequired(),
                                     NumberRange(_WORLD_MIN_SIZE, _WORLD_MAX_SIZE)])

    serial = IntegerField("Перейти к поколению",
                          default=lambda: _get_default_value('serial', 0),
                          validators=[InputRequired(),
                                      NumberRange(min=0, max=9999)])

    autoupdate = BooleanField("Автоматическое обновление",
                              default=lambda: _get_default_value('autoupdate', True))

    update_period = SelectField("Период обновления",
                                default=lambda: _get_default_value('update_period', 1000),
                                choices=((2000, "2 сек"), (1000, "1 сек"),
                                         (500, "0.5 сек"), (250, "0.25 сек"), (100, "0.1 сек")),
                                coerce=int)

    disable_js = BooleanField("Не загружать js скрипты",
                              default=lambda: _get_default_value('disable_js', False),
                              description="При включении этой опции автоматическое обновление работать не будет.")

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
            # TODO: How do get a list of form fields?
            names = ("height", "width", "serial", "autoupdate", "update_period", "disable_js")
            for name in names:
                self._context_data[name] = getattr(self, name).data
        return result


def _get_default_value(name: str, default):
    # TODO: This is a workaround. I don't understand how to pass the session context data
    #  to the form fields in the initiator of the form object.
    context_data = SessionService().get_session_context().get_dict(WorldSizeForm)
    return context_data.get(name, default)
