from enum import Enum


class SignupTypeEnum(Enum):
    DATE_LOCATION_TIME_SLOT = 1
    DATE_TIME_SLOT = 2
    RSVP_ADULT_CHILD = 3
    RSVP = 4
    SLOT_DATETIME = 5
