import importlib

from bs4 import BeautifulSoup

from .errors import UnsupportedVariant
from .enums import SignupTypeEnum


PARSERS = {
    SignupTypeEnum.RSVP: "signup_genius.parsers.rsvp",
    SignupTypeEnum.RSVP_ADULT_CHILD: "signup_genius.parsers.rsvp_adult_child",
    SignupTypeEnum.DATE_TIME_SLOT: "signup_genius.parsers.date_time_slot",
    SignupTypeEnum.DATE_LOCATION_TIME_SLOT: "signup_genius.parsers.date_location_time_slot",
    SignupTypeEnum.SLOT_DATETIME: "signup_genius.parsers.slot_datetime",
}


class Introspector:
    def __init__(self, soup):
        self.soup = soup
        self.type = self._introspect()

    @classmethod
    def from_html(cls, html):
        return cls(BeautifulSoup(html, "html.parser"))

    @classmethod
    def from_path(cls, path):
        return cls.from_html(open(path).read())

    def parser(self):
        module_path = PARSERS.get(self.type)
        mod = importlib.import_module(module_path)
        cls = getattr(mod, "Parser")
        return cls(self.soup)

    def _introspect(self):
        ret = None

        count_outer_tables = self._count_by_selector("table.SUGtableouter")
        count_headers = self._count_by_selector("td.SUGtableheader")

        if count_outer_tables == 2:
            if self.soup.find(string="Guest Count:"):
                ret = SignupTypeEnum.RSVP
            else:
                ret = SignupTypeEnum.RSVP_ADULT_CHILD
        elif count_outer_tables == 1:
            if count_headers == 2:
                ret = SignupTypeEnum.SLOT_DATETIME
            elif count_headers == 3:
                ret = SignupTypeEnum.DATE_TIME_SLOT
            elif count_headers == 4:
                ret = SignupTypeEnum.DATE_LOCATION_TIME_SLOT
        if ret is None:
            raise UnsupportedVariant()
        return ret

    def _count_by_selector(self, selector):
        return len(self.soup.select(selector))
