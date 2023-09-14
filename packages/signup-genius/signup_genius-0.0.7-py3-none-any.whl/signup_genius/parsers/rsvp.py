from dataclasses import dataclass
import logging
import re

from signup_genius.errors import ParseError

from . import BaseParser

logger = logging.getLogger(__name__)


class Parser(BaseParser):
    def parse(self):
        signups = []
        for response, selector, parse_method in [
            ("Yes", "div#subcatY", self._parse_one_signup_with_counts),
            ("No", "div#subcatN", self._parse_one_signup_without_counts),
            ("Maybe", "div#subcatM", self._parse_one_signup_with_counts),
            ("NoResponse", "div#subcatR", self._parse_one_no_response_signup),
        ]:
            if elem := self.soup.select_one(selector):
                signups.extend(self._parse_section(parse_method, response, elem))
            else:
                logger.warning(f"No element found for {response=}, {selector=}")
        return signups

    def _parse_section(self, parse_method, response, elem):
        signups = []
        for td in elem.select("td:nth-of-type(2)"):
            if signup := parse_method(response, td):
                signups.append(signup)
        return signups

    def _parse_one_signup_without_counts(self, response, td):
        name = td.select_one("strong").text.strip()
        comments = ""
        if comment_elem := td.select_one("span"):
            comments = comment_elem.text.strip()
        return Signup(response, name, comments, guest_count=0)

    def _parse_one_signup_with_counts(self, response, td):
        supplied_name = td.select_one("strong").text.strip()
        comments = ""
        if comment_elem := td.select_one("span"):
            comments = comment_elem.text.strip()
        try:
            name, guest_count = self._parse_supplied_name(supplied_name)
            return Signup(response, name, comments, guest_count)
        except ParseError as ex:  # pragma: no cover
            logger.error(ex)
            return None

    def _parse_one_no_response_signup(self, response, td):
        name = td.text.strip()
        return Signup(response, name, comments="", guest_count=0)

    def _parse_supplied_name(self, raw):
        if match := re.match(r"^(?P<name>.*?)[\n ]*\((?P<count>\d+) guest", raw):
            name, count = match.group("name"), match.group("count")
            count = int(count) if count else 0
        return name, count


@dataclass
class Signup:
    response: str
    name: str
    comments: str
    guest_count: int
