import pytest

from signup_genius.api import get_signups_from_api, CachingSignupApiWrapper


@pytest.fixture
def caching_api_wrapper(api_cache_path):
    return CachingSignupApiWrapper(
        cache_dir=api_cache_path, refresh=False, never_refresh=True
    )


def test_warriors_api(caching_api_wrapper):
    url_id = "5080C48A4AC2FA13-warrriors"
    signups = get_signups_from_api(url_id, api_wrapper=caching_api_wrapper)
    assert len(signups) > 0
    assert caching_api_wrapper.request_count == 0


def test_pinewood_derby_api(caching_api_wrapper):
    url_id = "5080c48a4ac2fa13-pinewood"
    signups = get_signups_from_api(url_id, api_wrapper=caching_api_wrapper)
    slots = {signup.slot for signup in signups}
    for slot in slots:
        print(slot.name)
    assert len(slots) == 12
    assert caching_api_wrapper.request_count == 0
