import datetime


from signup_genius import get_signups, get_signups_from_html


def test_signups_from_manresa():
    signups = get_signups(
        "https://www.signupgenius.com/go/10c0c4aa8a82cabfdc61-manresa"
    )
    assert len(signups) > 0


def test_signups_from_api_warriors():
    signups = get_signups(
        "https://www.signupgenius.com/go/5080c48a4ac2fa13-warrriors#/"
    )
    assert len(signups) > 0


def test_signups_from_html(date_time_slot):
    signups = get_signups_from_html(date_time_slot.read_text())
    assert len(signups) == 151
    assert sum(s.count for s in signups) == 191
    assert signups[0].name == "Betty Bethune"
    assert hasattr(signups[0], "slot"), "Signup should have a slot"
    assert signups[0].slot.date == datetime.date(2022, 10, 5)


def test_signups_from_html_with_name_mapping(date_time_slot):
    name_mapping = {"John Hertel": "John B. Hertel"}
    signups = get_signups_from_html(
        date_time_slot.read_text(), name_mapping=name_mapping
    )
    names = {s.name for s in signups}
    assert "John B. Hertel" in names
    assert "John Hertel" not in names


def test_signups_from_html_with_fuzzy_match(date_time_slot):
    match_names = ["John B. Hertel", "Another Person"]
    signups = get_signups_from_html(date_time_slot.read_text(), match_names=match_names)
    names = {s.name for s in signups}
    assert "John B. Hertel" in names
    assert "John Hertel" not in names


def test_signups_from_html_with_name_mapping_and_fuzzy_match(date_time_slot):
    name_mapping = {"John Hertel": "John B. Hertel"}
    match_names = ["Another Person"]
    signups = get_signups_from_html(
        date_time_slot.read_text(), name_mapping=name_mapping, match_names=match_names
    )
    names = {s.name for s in signups}
    assert (
        "John B. Hertel" in names
    ), "explicit name mappings should be ignored by any later match to known names"
    assert "John Hertel" not in names
