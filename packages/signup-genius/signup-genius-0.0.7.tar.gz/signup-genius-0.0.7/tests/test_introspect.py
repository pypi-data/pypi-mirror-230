from signup_genius.introspect import Introspector
from signup_genius.enums import SignupTypeEnum


def test_introspect_date_time_slot(date_time_slot):
    introspector = Introspector.from_path(date_time_slot)
    assert introspector.type == SignupTypeEnum.DATE_TIME_SLOT


def test_introspect_date_location_time_slot(date_location_time_slot):
    introspector = Introspector.from_path(date_location_time_slot)
    assert introspector.type == SignupTypeEnum.DATE_LOCATION_TIME_SLOT


def test_introspect_rsvp(rsvp):
    introspector = Introspector.from_path(rsvp)
    assert introspector.type == SignupTypeEnum.RSVP


def test_introspect_rsvp_adult_child(rsvp_adult_child):
    introspector = Introspector.from_path(rsvp_adult_child)
    assert introspector.type == SignupTypeEnum.RSVP_ADULT_CHILD


def test_introspect_rsvp_adult_child_parser(rsvp_adult_child):
    introspector = Introspector.from_path(rsvp_adult_child)
    parser = introspector.parser()
    signups = parser.parse()
    assert len(signups) == 78


def test_slot_datetime(slot_datetime):
    introspector = Introspector.from_path(slot_datetime)
    assert introspector.type == SignupTypeEnum.SLOT_DATETIME
