from flask_wtf import FlaskForm
from flask_wtf.file import MultipleFileField
from wtforms import StringField, SubmitField, URLField
from wtforms.validators import (
    DataRequired,
    Length,
    Optional,
    Regexp,
    URL,
    ValidationError
)

from .constants import (
    MIN_LENGTH,
    ORIGINAL_LINK_MAX_LENGTH,
    REGEXP,
    SHORT_LINK_MAX_LENGTH
)


class URLMapForm(FlaskForm):
    original_link = URLField(
        'Длинная ссылка',
        validators=[
            DataRequired(message='Обязательное поле'),
            Length(MIN_LENGTH, ORIGINAL_LINK_MAX_LENGTH),
            URL(message='Некорректный URL')
        ]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Length(max=SHORT_LINK_MAX_LENGTH),
            Optional(),
            Regexp(
                regex=REGEXP,
                message='Указано недопустимое имя для короткой ссылки'
            )
        ]
    )
    submit = SubmitField('Создать')


class UploadForm(FlaskForm):
    files = MultipleFileField('Выберите файлы')
    submit = SubmitField('Загрузить')

    def validate_files(self, field):
        if not field.data or (
            len(field.data) == MIN_LENGTH and field.data[0].filename == ''
        ):
            raise ValidationError('Необходимо выбрать хотя бы один файл.')
