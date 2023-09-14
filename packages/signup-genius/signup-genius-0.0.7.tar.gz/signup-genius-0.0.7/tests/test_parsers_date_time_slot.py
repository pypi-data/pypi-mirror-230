import datetime

from bs4 import BeautifulSoup

from signup_genius.parsers.date_time_slot import Parser


def test_date_time_slot(date_time_slot):
    html = open(date_time_slot).read()
    html = html.replace(
        '<!--<div><span class="glyphicon glyphicon-ok-sign SUGicon"></span>-->',
        '<div><!--<span class="glyphicon glyphicon-ok-sign SUGicon"></span>-->',
    )
    soup = BeautifulSoup(html, "html.parser")
    parser = Parser(soup)
    signups = parser.parse()
    assert len(signups) == 151
    assert sum(s.count for s in signups) == 191
    assert hasattr(signups[0], "slot"), "Signup should have a slot"
    assert signups[0].slot.date == datetime.date(2022, 10, 5)
    assert signups[0].comments == "Nothing to see here"

    for signup in signups:
        if (
            signup.slot.time == "5:30pm - 7:30pm"
            and signup.slot.name == "Operational Team"
        ):
            assert signup.slot.date == datetime.date(
                2022, 10, 6
            ), "Testing that rowspan dates are carried forward correctly"
            break
