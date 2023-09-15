import re
from typing import Set, Iterable, Tuple


class ScopeError(ValueError):
    pass


class ScopeValidationError(ScopeError):
    pass


class ScopeAuthorizationError(ScopeError):
    pass


FIXED_SCOPES = {
    "av",
    "av:ro",
    "av:hosting",
    "av:hosting:ro",
    "av:mailbox",
    "av:ai",
    "av:ai:engine",
    "av:ai:engine:chat",
    "av:ai:ro",
    "av:ai:engine:ro",
    "av:ai:engine:chat:ro",
    "av:services",
    "av:services:ro",
    "av:serviceGroups",
    "av:serviceGroups:ro",
}

FIXED_REGEXES = [
    re.compile(r"^av:hosting:agent1[qpzry9x8gf2tvdw0s3jn54khce6mua7l]{59}$"),
    re.compile(r"^av:mailbox:agent1[qpzry9x8gf2tvdw0s3jn54khce6mua7l]{59}$"),
    re.compile(
        r"^av:(?:services|serviceGroups|ai:engine:chat):[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}(?::ro)?$"
    ),
]


def validate_scope(value: str):
    # check the fixed patterns
    if value in FIXED_SCOPES:
        return

    # check each of the regexes
    for pattern in FIXED_REGEXES:
        if pattern.match(value) is not None:
            return

    raise ScopeValidationError(f"Invalid scope: {value}")


def validate_scopes(values: Iterable[str]):
    for value in values:
        validate_scope(value)


def parse_scopes(value: str) -> Set[str]:
    tokens = set(value.split())
    validate_scopes(tokens)
    return tokens


def normalise_scopes(value: str | Set[str]) -> str:
    if isinstance(value, str):
        scopes = parse_scopes(value)
    else:
        scopes = value

    return " ".join(sorted(scopes))


def _extract_read_only(value: str) -> Tuple[str, bool]:
    read_only = False
    if value.endswith(":ro"):
        value = value[:-3]
        read_only = True
    return value, read_only


def _authorize_scope(scope: str, requirement: str) -> bool:

    # strip and remove the read only flags from the requirement
    scope, scope_ro = _extract_read_only(scope)
    requirement, requirement_ro = _extract_read_only(requirement)

    # if the requirement is NOT read only, but the scope
    if scope_ro and not requirement_ro:
        return False

    # split the scope into a tree
    requirement_tree = requirement.split(":")
    scope_tree = scope.split(":")

    # if the scope has LOWER permissions than the requirement tree, then this
    # is an automatic auth failure
    if len(scope_tree) > len(requirement_tree):
        return False

    common_tree_len = min(len(scope_tree), len(requirement_tree))
    authorized = scope_tree[:common_tree_len] == requirement_tree[:common_tree_len]

    return authorized


def authorize_scope(
    scope: str, requirement: str, *, raise_exception: bool = True
) -> bool:
    success = _authorize_scope(scope, requirement)
    if not success and raise_exception:
        raise ScopeAuthorizationError()

    return success


def authorize_scopes(scopes: str | Set[str], requirement: str) -> bool:
    if isinstance(scopes, str):
        scopes = parse_scopes(scopes)

    success = False
    for scope in scopes:
        if authorize_scope(scope, requirement, raise_exception=False):
            success = True
            break

    if not success:
        raise ScopeAuthorizationError()

    return True
