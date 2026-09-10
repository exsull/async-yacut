from http import HTTPStatus
import re

from flask import jsonify, request, url_for
from sqlalchemy.exc import IntegrityError

from . import app, db
from .constants import MIN_LENGTH, REGEXP, SHORT_LINK_MAX_LENGTH
from .error_handlers import (
    BadCustomIdError,
    CustomIdIsFilesError,
    DuplicatedShortIdError,
    IncorrectUrlError,
    InvalidAPIUsage,
    MissingBodyError,
    MissingUrlError
)
from .models import URLMap
from .utils import get_unique_short_id
from .validators import is_valid_url


def validate_and_get_custom_id(custom_id):
    if not isinstance(custom_id, str):
        raise BadCustomIdError()

    if custom_id == '':
        return get_unique_short_id(URLMap)

    if (
        not MIN_LENGTH <= len(custom_id) <= SHORT_LINK_MAX_LENGTH
        or not re.fullmatch(REGEXP, custom_id)
    ):
        raise BadCustomIdError()

    if custom_id == 'files':
        raise CustomIdIsFilesError()

    if URLMap.query.filter_by(short=custom_id).first():
        raise DuplicatedShortIdError()

    return custom_id


@app.route('/api/id/', methods=['POST'])
def create_url():
    """Создание короткой ссылки."""
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        raise MissingBodyError()

    if 'url' not in data:
        raise MissingUrlError()

    original = data['url']

    if not is_valid_url(original):
        raise IncorrectUrlError()

    if 'custom_id' in data and data['custom_id'] is not None:
        short = validate_and_get_custom_id(data['custom_id'])
    else:
        short = get_unique_short_id(URLMap)

    url_map = URLMap(
        original=original,
        short=short,
    )

    try:
        db.session.add(url_map)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            'error': 'Не удалось создать короткую ссылку'
        }), HTTPStatus.INTERNAL_SERVER_ERROR

    link = url_for(
        'redirect_view',
        short=short,
        _external=True,
    )

    return jsonify({
        'url': url_map.original,
        'short_link': link,
    }), HTTPStatus.CREATED


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_original(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first()
    if not url_map:
        raise InvalidAPIUsage('Указанный id не найден', HTTPStatus.NOT_FOUND)
    return jsonify(url=url_map.original), HTTPStatus.OK
