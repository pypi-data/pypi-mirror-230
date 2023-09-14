import mimetypes
from urllib.parse import urljoin, urlparse

TEXT_FILE_TYPES = [
    'text/css',
    'text/csv',
    'text/calendar',
    'application/javascript',
    'text/javascript',
    'text/plain',
    'text/xml']


def static_url(url):
    """Return True if url is static: CSS, JS, etc. """
    # Remove query parameters
    noparams = urljoin(url, urlparse(url).path)
    ftype = mimetypes.guess_type(noparams)[0]
    if ftype in TEXT_FILE_TYPES:
        return True
    else:
        return False

