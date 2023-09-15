from followthemoney.proxy import E
from followthemoney.types import registry

from nomenklatura.matching.v1.util import has_disjoint, has_overlap
from nomenklatura.matching.v1.util import compare_levenshtein, tokenize_pair
from nomenklatura.matching.util import extract_numbers, props_pair, type_pair
from nomenklatura.matching.util import compare_sets, has_schema
from nomenklatura.util import normalize_name


def birth_place(left: E, right: E) -> float:
    """Same place of birth."""
    lv, rv = tokenize_pair(props_pair(left, right, ["birthPlace"]))
    tokens = min(len(lv), len(rv))
    return float(len(lv.intersection(rv))) / float(max(2.0, tokens))


def address_match(left: E, right: E) -> float:
    """Text similarity between addresses."""
    lv, rv = type_pair(left, right, registry.address)
    lvn = [normalize_name(v) for v in lv]
    rvn = [normalize_name(v) for v in rv]
    return compare_sets(lvn, rvn, compare_levenshtein)


def address_numbers(left: E, right: E) -> float:
    """Find if names contain numbers, score if the numbers are different."""
    lv, rv = type_pair(left, right, registry.address)
    lvn = extract_numbers(lv)
    rvn = extract_numbers(rv)
    common = len(lvn.intersection(rvn))
    disjoint = len(lvn.difference(rvn))
    return common - disjoint


def gender_mismatch(left: E, right: E) -> float:
    """Both entities have a different gender associated with them."""
    lv, rv = props_pair(left, right, ["gender"])
    return has_disjoint(lv, rv)


def phone_match(left: E, right: E) -> float:
    """Matching phone numbers between the two entities."""
    lv, rv = type_pair(left, right, registry.phone)
    return has_overlap(set(lv), set(rv))


def email_match(left: E, right: E) -> float:
    """Matching email addresses between the two entities."""
    lv, rv = type_pair(left, right, registry.email)
    return has_overlap(set(lv), set(rv))


def identifier_match(left: E, right: E) -> float:
    """Matching identifiers (e.g. passports, national ID cards, registration or
    tax numbers) between the two entities."""
    if has_schema(left, right, "Organization"):
        return 0.0
    lv, rv = type_pair(left, right, registry.identifier)
    return has_overlap(set(lv), set(rv))


def org_identifier_match(left: E, right: E) -> float:
    """Matching identifiers (e.g. registration or tax numbers) between two
    organizations or companies."""
    if not has_schema(left, right, "Organization"):
        return 0.0
    lv, rv = type_pair(left, right, registry.identifier)
    return has_overlap(set(lv), set(rv))


def country_mismatch(left: E, right: E) -> float:
    """Both entities are linked to different countries."""
    lv, rv = type_pair(left, right, registry.country)
    return has_disjoint(set(lv), set(rv))
