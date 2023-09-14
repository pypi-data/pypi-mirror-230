from dataclasses import dataclass

from signup_genius.errors import ParseError

from .date_time_slot import Parser as DateTimeSlotParser


class Parser(DateTimeSlotParser):
    def _get_rows(self, soup):
        date_stack = []
        location_stack = []
        for elem in soup.select(".SUGtableouter tr td.SUGtable:first-of-type"):
            td_cells = [
                *elem.find_previous_siblings("td"),
                elem,
                *elem.find_next_siblings("td"),
            ]
            if len(td_cells) == 4:
                date_text = td_cells[0].text.strip()
                location_text = td_cells[1].text.strip()
                time_text = td_cells[2].text.strip()
                slots_elem = td_cells[3]
                if rowspan := td_cells[0].get("rowspan"):
                    rowspan = int(rowspan)
                    date_stack = [date_text for _ in range(rowspan - 1)]
                if rowspan := td_cells[1].get("rowspan"):
                    rowspan = int(rowspan)
                    location_stack = [location_text for _ in range(rowspan - 1)]
            elif len(td_cells) == 3:
                if not date_stack:  # pragma: no cover
                    raise ParseError(
                        "No date td and no rowspan > 1 from previous row(s)"
                    )
                date_text = date_stack.pop()
                location_text = td_cells[0].text.strip()
                time_text = td_cells[1].text.strip()
                slots_elem = td_cells[2]
            elif len(td_cells) == 2:
                if not date_stack:  # pragma: no cover
                    raise ParseError(
                        "No date td and no rowspan > 1 from previous row(s)"
                    )
                if not location_stack:  # pragma: no cover
                    raise ParseError(
                        "No location td and no rowspan > 1 from previous row(s)"
                    )
                date_text = date_stack.pop()
                location_text = location_stack.pop()
                time_text = td_cells[0].text.strip()
                slots_elem = td_cells[1]
            else:  # pragma: no cover
                raise ParseError(
                    f"Unexpected number of table cells for a row ({len(td_cells)})"
                )
            yield Row(date_text, location_text, time_text), slots_elem

    def _create_slot(self, row, name, capacity, comments):
        date = self._parse_date(row.date)
        return Slot(date, row.location, row.time, name, capacity, comments)


@dataclass
class Row:
    date: str
    location: str
    time: str


@dataclass
class Slot:
    date: str
    location: str
    time: str
    name: str
    comments: str = ""
    capacity: int = 1
    filled: int = 0
