from signup_genius.name_mapping import (
    update_signups_from_name_mapping,
    update_signups_fuzzy_match,
    get_updated_signups,
    get_updated_names,
)


def test_name_map(signups):
    mapping = {"Bradley Jones": "Brad Jones"}
    update_signups_from_name_mapping(signups, mapping)
    updated_signups = get_updated_signups(signups)
    assert len(updated_signups) == 1
    assert updated_signups[0].name == "Brad Jones"
    assert updated_signups[0]._original_name == "Bradley Jones"


def test_name_map_case_insensitive(signups):
    mapping = {"Declan Wright": "Declan J. Wright"}
    update_signups_from_name_mapping(signups, mapping)
    updated_signups = get_updated_names(signups)
    assert len(updated_signups) == 1
    assert updated_signups[0].name == "Declan J. Wright"
    assert updated_signups[0].original_name == "declan wright"


def test_name_map_empty_mapping(signups):
    mapping = {}
    update_signups_from_name_mapping(signups, mapping)
    updated_signups = get_updated_names(signups)
    assert len(updated_signups) == 0


def test_name_map_no_matches(signups):
    mapping = {"John Doe": "Jonathan Doe"}
    update_signups_from_name_mapping(signups, mapping)
    updated_signups = get_updated_names(signups)
    assert len(updated_signups) == 0


def test_fuzzy_update(signups, known_names):
    update_signups_fuzzy_match(signups, known_names)
    updated_signups = get_updated_signups(signups)
    assert len(updated_signups) == 5
    assert {s.name for s in signups} == set(known_names)
