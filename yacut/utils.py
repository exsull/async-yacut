import secrets
import string

from flask import url_for

from . import db
from .constants import SHORT_CODE_MAX_LENGTH
from .models import URLMap
from .yandex_disk import (
    get_download_url,
    get_upload_url,
    upload_file,
)


def get_unique_short_id(model, length=SHORT_CODE_MAX_LENGTH):
    """Генерирует уникальный короткий идентификатор."""
    characters = string.ascii_letters + string.digits

    while True:
        short = ''.join(
            secrets.choice(characters)
            for _ in range(length)
        )

        if not model.query.filter_by(short=short).first():
            return short


async def process_file(session, file):
    """Загрузить один файл и получить ссылку для скачивания."""
    upload_url = await get_upload_url(
        session,
        file.filename,
    )

    disk_path = await upload_file(
        session,
        file,
        upload_url,
    )

    download_url = await get_download_url(
        session,
        disk_path,
    )

    short = get_unique_short_id(URLMap)

    while (
        short == 'files'
        or URLMap.query.filter_by(short=short).first() is not None
    ):
        short = get_unique_short_id(URLMap)

    url_map = URLMap(
        original=download_url,
        short=short,
    )

    db.session.add(url_map)

    return file.filename, url_for(
        'redirect_view',
        short=short,
        _external=True,
    )
