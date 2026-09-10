from urllib.parse import unquote
from uuid import uuid4

from . import app


API_HOST = 'https://cloud-api.yandex.net/'
API_VERSION = 'v1'

REQUEST_UPLOAD_URL = (
    f'{API_HOST}{API_VERSION}/disk/resources/upload'
)

DOWNLOAD_LINK_URL = (
    f'{API_HOST}{API_VERSION}/disk/resources/download'
)

DISK_TOKEN = app.config['DISK_TOKEN']

AUTH_HEADERS = {'Authorization': f'OAuth {DISK_TOKEN}'}


async def get_upload_url(session, filename):
    """Получить URL для загрузки файла."""
    payload = {
        'path': f'app:/{uuid4()}_{filename}',
        'overwrite': 'False',
    }

    async with session.get(
        REQUEST_UPLOAD_URL,
        headers=AUTH_HEADERS,
        params=payload,
    ) as response:
        response.raise_for_status()
        data = await response.json()

    return data['href']


async def upload_file(session, file, upload_url):
    """Загрузить файл на Яндекс Диск."""
    file_stream = getattr(file, 'stream', file)
    file_stream.seek(0)

    file_data = file_stream.read()

    async with session.put(
        upload_url,
        data=file_data,
    ) as response:
        response.raise_for_status()

    location = response.headers['Location']
    return unquote(location).replace('/disk', '', 1)


async def get_download_url(session, disk_path):
    """Получить ссылку на скачивание файла."""
    async with session.get(
        DOWNLOAD_LINK_URL,
        headers=AUTH_HEADERS,
        params={'path': disk_path},
    ) as response:
        response.raise_for_status()
        data = await response.json()

    return data['href']
