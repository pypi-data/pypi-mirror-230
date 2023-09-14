from dataclasses import dataclass
import dateutil.parser
import re


from signup_genius.errors import ParseError

from . import BaseParser


class Parser(BaseParser):
    def parse(self):
        signups = []
        for row, slots_elem in self._get_rows(self.soup):
            for slot, slot_elem in self._get_slots_for_row(row, slots_elem):
                _signups = self._get_signups_for_slot(slot, slot_elem)
                signups.extend(_signups)
        return signups

    def _get_rows(self, soup):
        date_stack = []
        for elem in soup.select(".SUGtableouter tr td.SUGtable:first-of-type"):
            td_cells = [
                *elem.find_previous_siblings("td"),
                elem,
                *elem.find_next_siblings("td"),
            ]
            if len(td_cells) == 3:
                date_text = td_cells[0].text.strip()
                time_text = td_cells[1].text.strip()
                slots_elem = td_cells[2]
                if rowspan := td_cells[0].get("rowspan"):
                    rowspan = int(rowspan)
                    date_stack = [date_text for _ in range(rowspan - 1)]
            elif len(td_cells) == 2:
                if not date_stack:  # pragma: no cover
                    raise ParseError(
                        "No date td and no rowspan > 1 from previous row(s)"
                    )
                date_text = date_stack.pop()
                time_text = td_cells[0].text.strip()
                slots_elem = td_cells[1]
            yield Row(date_text, time_text), slots_elem

    def _get_slots_for_row(self, row, slots_elem):
        for elem in slots_elem.select(".SUGtableouter tr td:last-of-type p.SUGbigbold"):
            tr = elem.parent.parent
            first_td = tr.select_one("td:first-of-type")
            last_td = tr.select_one("td:last-of-type")

            name, capacity = self._get_slot_name(first_td)
            comments = self._get_slot_comments(first_td)
            slot = self._create_slot(row, name, capacity, comments)
            yield slot, last_td

    def _get_signups_for_slot(self, slot, slot_elem):
        signups_elem = slot_elem
        slots_filled_elem = signups_elem.select_one("div span.SUGbigbold")

        slots_filled = 0
        if slots_filled_elem:
            slots_filled_str = slots_filled_elem.text.strip().split()[0]
            if slots_filled_str == "All":
                slots_filled = slot.capacity
            else:
                slots_filled = int(slots_filled_str)

        signups = []
        for elem in signups_elem.select("table"):
            count, comment = 1, ""
            name_span = elem.select_one("span.SUGsignups")
            name = name_span.text.replace("\n", "").replace("\t", "").strip()
            if match := re.search(r"^(.*?)\((\d+)\)$", name, re.M):
                name = match.group(1).strip()
                count = int(match.group(2))
            if comment_span := elem.select_one("div.SUGMemberComment"):
                comment = comment_span.text.strip()
            signups.append(Signup(name, count, comment, slot))

        if (
            slot.capacity == 1 and len(signups) == 1 and slots_filled == 0
        ):  # pragma: no cover
            # seems to be no '1 of 1 filled' when capacity is 1
            slots_filled = 1
        slot.filled = slots_filled
        return signups

    def _get_slot_name(self, elem):
        found = elem.select_one("p.SUGbigbold")
        if not found:  # pragma: no cover
            raise ParseError("No slot name found")
        return self._parse_slot_name(found.text.strip())

    def _parse_slot_name(self, raw):
        if match := re.match(r"^(?P<name>.*?) \((?P<count>\d+)\)$", raw):
            name = match.group("name")
            count = int(match.group("count"))
        else:
            name = raw
            count = 1
        return name, count

    def _get_slot_comments(self, elem):
        found = elem.select_one("div.SUGcomment")
        return found.text.strip() if found else ""

    def _parse_date(self, raw):
        """10/05/2022 (Wed.)"""
        return dateutil.parser.parse(raw.split(" ")[0]).date()

    def _create_slot(self, row, name, capacity, comments):
        date = self._parse_date(row.date)
        return Slot(date, row.time, name, capacity, comments)


@dataclass
class Row:
    date: str
    time: str


@dataclass
class Slot:
    date: str
    time: str
    name: str
    comments: str = ""
    capacity: int = 1
    filled: int = 0


@dataclass
class Signup:
    name: str
    count: int
    comments: str
    slot: Slot
