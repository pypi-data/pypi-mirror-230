import datetime

from bs4 import BeautifulSoup

from signup_genius.parsers.slot_datetime import Parser


def test_slot_datetime(slot_datetime):
    html = open(slot_datetime).read()
    soup = BeautifulSoup(html, "html.parser")
    parser = Parser(soup)
    signups = parser.parse()
    assert len(signups) == 39

    # assert sum(s.count for s in signups) == 162
    # assert hasattr(signups[0], "slot"), "Signup should have a slot"
    # assert signups[0].slot.date == datetime.date(2022, 10, 15)
    # assert signups[0].slot.location == "Lake Chabot"
