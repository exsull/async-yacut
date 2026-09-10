from urllib.parse import urlparse


def is_valid_url(url):
    """Проверяет, что строка является корректным URL."""
    if not isinstance(url, str) or not url.strip():
        return False

    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
    except ValueError:
        return False

    return (
        parsed.scheme in ('http', 'https')
        and bool(parsed.netloc)
        and bool(hostname)
        and ' ' not in hostname
    )
