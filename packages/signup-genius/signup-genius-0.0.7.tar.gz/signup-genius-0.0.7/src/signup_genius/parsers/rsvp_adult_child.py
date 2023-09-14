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
        return Signup(response, name, comments, adult_count=0, child_count=0)

    def _parse_one_signup_with_counts(self, response, td):
        supplied_name = td.select_one("strong").text.strip()
        comments = ""
        if comment_elem := td.select_one("span"):
            comments = comment_elem.text.strip()
        try:
            name, adult_count, child_count = self._parse_supplied_name(supplied_name)
            return Signup(response, name, comments, adult_count, child_count)
        except ParseError as ex:  # pragma: no cover
            logger.error(ex)
            return None

    def _parse_one_no_response_signup(self, response, td):
        name = td.text.strip()
        return Signup(response, name, comments="", adult_count=0, child_count=0)

    def _parse_supplied_name(self, raw):
        if match := re.match(r"^(?P<name>.*?)[\n ]*\((?P<counts>.*?)\)", raw):
            name, counts = match.group("name"), match.group("counts")
            adult_count, child_count = 0, 0
            for piece in re.split(r", ", counts):
                bits = piece.split(" ", 1)
                if len(bits) != 2:  # pragma: no cover
                    raise ParseError(
                        f"Expected something like '1 adult', but got {piece!r}"
                    )
                count, adult_or_child = bits
                count = int(count) if count else 0
                if adult_or_child.startswith("adult"):
                    adult_count = count
                elif adult_or_child.startswith("child"):
                    child_count = count
            return name, adult_count, child_count
        raise ParseError(f"Failed to parse name from {raw}")


@dataclass
class Signup:
    response: str
    name: str
    comments: str
    adult_count: int
    child_count: int
