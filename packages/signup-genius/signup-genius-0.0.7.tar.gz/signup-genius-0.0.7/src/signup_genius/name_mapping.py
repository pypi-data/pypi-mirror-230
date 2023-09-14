from collections import namedtuple
from dataclasses import dataclass
import functools
import logging

from Levenshtein import distance

logger = logging.getLogger(__name__)

UpdatedName = namedtuple("UpdatedName", "original_name name")


def update_signups_from_name_mapping(signups, mapping):
    """Update signup names from a mapping"""
    lowercased = {k.lower(): v for k, v in mapping.items()}
    for signup in signups:
        mapped_name = lowercased.get(signup.name.lower())
        if mapped_name:
            signup._original_name = signup.name
            signup.name = mapped_name
    return signups


def update_signups_to_known_names_matching_case(signups, names):
    lowercased = {n.lower(): n for n in names}
    for signup in signups:
        mapped_name = lowercased.get(signup.name.lower())
        if mapped_name and mapped_name != signup.name:
            signup._original_name = signup.name
            signup.name = mapped_name
    return signups


def unresolved(signups, names):
    """return signups whose names are not found within the names collection"""
    names = set(n.lower() for n in names)
    unresolved = []
    for signup in signups:
        if signup.name.lower() not in names:
            unresolved.append(signup)
    return unresolved


def update_signups_fuzzy_match(signups, names, dryrun=False):
    """Update signup names based on fuzzy matching to a collection of known names"""
    # first normalize case
    update_signups_to_known_names_matching_case(signups, names)
    for signup in unresolved(signups, names):
        distances = []
        for name in names:
            distances.append(
                NameDistance(name, calc_distance(signup.name.lower(), name.lower()))
            )
        closest = min(distances, key=lambda i: i.distance)
        tied_closest = [d for d in distances if d.distance == closest.distance]
        logger.debug(
            f"{len(tied_closest)} closest matches for {signup.name}: {', '.join([_.name for _ in tied_closest])}"
        )
        if not dryrun and tied_closest:
            signup._original_name = signup.name
            signup.name = tied_closest[0].name


@functools.lru_cache(maxsize=None)
def calc_distance(s1, s2):
    return distance(s1.lower(), s2.lower())


def get_updated_signups(signups):
    """for a collection of signups, return the subset whose names have been updated"""
    return [s for s in signups if hasattr(s, "_original_name")]


def get_updated_names(signups):
    """for a collection of signups, return a set of original_name / updated name tuples
    to show what has been updated"""
    mapped = set(
        [UpdatedName(s._original_name, s.name) for s in get_updated_signups(signups)]
    )
    return sorted(mapped, key=lambda i: i[0])


@dataclass
class NameDistance:
    name: str
    distance: int
