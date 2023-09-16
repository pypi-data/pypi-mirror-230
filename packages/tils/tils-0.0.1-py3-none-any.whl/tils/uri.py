from urllib.parse import urlparse

def uri_validator(uri: str) -> bool:
    """Validates if a given string is a valid URI.

    Args:
        uri (str): URI to be validated.

    Returns:
        bool: True if the URI is valid, False otherwise.
    """
    # convert to string if not already
    if not isinstance(uri, str):
        uri = str(uri)

    # validate URI
    try:
        result = urlparse(uri)
        return all([result.scheme, result.netloc])
    except:
        return False