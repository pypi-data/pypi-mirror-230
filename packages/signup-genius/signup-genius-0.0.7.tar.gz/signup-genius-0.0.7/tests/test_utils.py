from signup_genius.utils import cache_file_for_url


def test_cache_file_for_url():
    url = "https://www.signupgenius.com/go/31f0d4daeaf2ca6ff2-testing"
    path = cache_file_for_url(url)
    assert path.suffix == ".htm"
    assert path.stem == "31f0d4daeaf2ca6ff2-testing"
