from urllib.parse import urlparse

def get_file_extension(url):
    """
    Extract the file extension from a URL.

    Parameters:
    url (str): The URL string.

    Returns:
    str: The file extension if present, otherwise an empty string.
    """
    parsed_url = urlparse(url)
    path = parsed_url.path
    if '.' in path:
        return path.split('.')[-1]
    return ''