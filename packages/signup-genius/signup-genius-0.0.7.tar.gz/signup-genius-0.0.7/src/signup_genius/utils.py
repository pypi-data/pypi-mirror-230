import pathlib
import tempfile


def cache_file_for_url(url):
    stem = url.split("/")[-1]
    return pathlib.Path(tempfile.gettempdir()) / f"{stem}.htm"
