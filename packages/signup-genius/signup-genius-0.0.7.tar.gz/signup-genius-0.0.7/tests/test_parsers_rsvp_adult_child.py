from bs4 import BeautifulSoup
from signup_genius.parsers.rsvp_adult_child import Parser


def test_parse_rsvp_adult_child(rsvp_adult_child):
    soup = BeautifulSoup(open(rsvp_adult_child).read(), "html.parser")
    parser = Parser(soup)
    signups = parser.parse()

    yes_signups = [s for s in signups if s.response == "Yes"]
    assert len(yes_signups) == 11
    assert sum(s.adult_count for s in yes_signups) == 8
    assert sum(s.child_count for s in yes_signups) == 12

    no_signups = [s for s in signups if s.response == "No"]
    assert len(no_signups) == 8
    assert all(s.adult_count == 0 for s in no_signups)
    assert all(s.child_count == 0 for s in no_signups)

    assert no_signups[0].name == "Helen Lucas"
    assert no_signups[0].comments == ""
    assert no_signups[2].name == "Sara Miller"
    assert no_signups[2].comments == "A comment"

    # no maybe signups in this genius
    maybe_signups = [s for s in signups if s.response == "Maybe"]
    assert len(maybe_signups) == 0

    no_response_signups = [s for s in signups if s.response == "NoResponse"]
    assert len(no_response_signups) == 59
    assert all(s.adult_count == 0 for s in no_response_signups)
    assert all(s.child_count == 0 for s in no_response_signups)
    assert no_response_signups[0].name == "Denise Davis"
    assert no_response_signups[-1].name == "Dennis Thompson"
