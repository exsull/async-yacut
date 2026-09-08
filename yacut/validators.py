from urllib.parse import urlparse


def is_valid_url(url):
    """Проверяет, что строка является корректным URL."""
    if not isinstance(url, str) or not url.strip():
        return False

    parsed = urlparse(url)

    return parsed.scheme in ('http', 'https') and bool(parsed.netloc)
