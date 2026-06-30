MAX_ESPNOW_PAYLOAD_BYTES = 240
PREFIX = ""

_TRIT_TO_CHAR = {-1: "-", 0: "0", 1: "+"}
_CHAR_TO_TRIT = {"-": -1, "0": 0, "+": 1}


def format_trits_payload(trits: list[int], max_payload_bytes: int = MAX_ESPNOW_PAYLOAD_BYTES) -> str:
    _validate_trits(trits)
    payload = PREFIX + "".join(_TRIT_TO_CHAR[trit] for trit in trits) + "\n"

    if len(payload.encode("utf-8")) > max_payload_bytes:
        raise ValueError(
            f"Payload too large for simple ESP-NOW mode "
            f"({len(payload.encode('utf-8'))} > {max_payload_bytes} bytes)."
        )

    return payload


def parse_trits_line(line: str) -> list[int]:
    line = line.strip()

    #if not line.startswith(PREFIX):
    #    raise ValueError("Invalid line: expected TRITS: prefix.")

    #line_removed_prefix = line.removeprefix(PREFIX)

    trits = []
    for c in line:
        if c not in _CHAR_TO_TRIT:
            raise ValueError(f"Invalid line: invalid trit value: {c!r}")
        trits.append(_CHAR_TO_TRIT[c])

    if not trits:
        raise ValueError("Invalid line: empty trits payload.")

    _validate_trits(trits)
    return trits


def _validate_trits(trits: list[int]) -> None:
    if any(trit not in (-1, 0, 1) for trit in trits):
        raise ValueError("Trits must contain only -1, 0 and 1.")

    if len(trits) % 6 != 0:
        raise ValueError("Trit count must be multiple of 6.")
