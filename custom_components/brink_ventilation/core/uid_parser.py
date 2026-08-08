"""Parser for Brink local UID values."""

from __future__ import annotations

from .uid_definitions import UID_DEFINITIONS, UID_LOOKUP, UIDDefinition


def decode_int(value: str) -> int:
    """Decode an integer value."""
    return int(value.split(",")[0])


def decode_bool(value: str) -> bool:
    """Decode a boolean value."""
    return decode_int(value) != 0


def decode_percent(value: str) -> int:
    """Decode a percentage."""
    return decode_int(value)


def decode_temperature(value: str) -> float:
    """Decode a temperature.

    Brink stores temperatures as tenths of a degree.
    Example:
        "231,0" -> 23.1
    """
    return decode_int(value) / 10


def decode_ascii(value: str) -> str:
    """Decode an ASCII string."""
    return bytes(
        number
        for number in map(int, value.split(","))
        if number != 0
    ).decode("ascii")


_UID_LOOKUP: dict[str, UIDDefinition] = {
    definition.uid: definition
    for definition in UID_DEFINITIONS
}


def parse_uid_values(
    values: dict[str, str],
) -> dict[str, object]:
    """Convert raw UID values into named values."""
    parsed: dict[str, object] = {}

    for uid, value in values.items():
        definition = UID_LOOKUP.get(int(uid.removeprefix("UID")))
        if definition is None:
            continue

        try:
            parsed[definition.key] = definition.decoder(value)
        except (TypeError, ValueError):
            parsed[definition.key] = value

    return parsed
