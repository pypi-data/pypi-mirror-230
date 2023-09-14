from bs4 import BeautifulSoup
from signup_genius.parsers.rsvp import Parser


def test_parse_rsvp(rsvp):
    soup = BeautifulSoup(open(rsvp).read(), "html.parser")
    parser = Parser(soup)
    signups = parser.parse()

    yes_signups = [s for s in signups if s.response == "Yes"]
    assert len(yes_signups) == 1
    assert sum(s.guest_count for s in yes_signups) == 2

    no_signups = [s for s in signups if s.response == "No"]
    assert len(no_signups) == 1

    # no maybe signups in this genius
    maybe_signups = [s for s in signups if s.response == "Maybe"]
    assert len(maybe_signups) == 0
