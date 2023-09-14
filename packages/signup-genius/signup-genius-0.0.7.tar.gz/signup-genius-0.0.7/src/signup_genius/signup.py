import logging
import requests

from bs4 import BeautifulSoup

from .introspect import Introspector
from .utils import cache_file_for_url
from .fixes import apply_html_fixes
from .name_mapping import update_signups_from_name_mapping, update_signups_fuzzy_match
from .api import get_signups_from_api, url_id_from_url, SignupApiError


logger = logging.getLogger(__name__)


def get_signups(
    url,
    refresh=True,
    fixes=True,
    name_mapping=None,
    match_names=None,
):
    cache = cache_file_for_url(url)
    if cache.exists() and not refresh:
        logger.info(f"Reading html from cache {cache}")
        html = cache.read_text()
    else:  # pragma: no cover
        logger.info(f"Requesting {url}")
        # try api first
        try:
            return _signups_from_api(
                url_id_from_url(url), name_mapping=name_mapping, match_names=match_names
            )
        except SignupApiError:
            pass
        # else fallback to parsing html
        resp = requests.get(url)
        html = resp.text
        with open(cache, "w") as f:
            f.write(html)
    return get_signups_from_html(
        html,
        fixes=fixes,
        name_mapping=name_mapping,
        match_names=match_names,
    )


def get_signups_from_html(html, fixes=True, name_mapping=None, match_names=None):
    if fixes:
        html = apply_html_fixes(html)
    return _signups_from_html(
        html,
        name_mapping=name_mapping,
        match_names=match_names,
    )


def _signups_from_api(url_id, name_mapping=None, match_names=None):
    signups = get_signups_from_api(url_id)
    if name_mapping:
        update_signups_from_name_mapping(signups, name_mapping)
    if match_names:
        # exclude any already explicitly mapped
        update_signups_fuzzy_match(
            [s for s in signups if not hasattr(s, "_original_name")], match_names
        )
    return signups


def _signups_from_html(html, name_mapping=None, match_names=None):
    soup = BeautifulSoup(html, "html.parser")
    introspector = Introspector(soup)
    parser = introspector.parser()
    signups = parser.parse()
    if name_mapping:
        update_signups_from_name_mapping(signups, name_mapping)
    if match_names:
        # exclude any already explicitly mapped
        update_signups_fuzzy_match(
            [s for s in signups if not hasattr(s, "_original_name")], match_names
        )
    return signups
