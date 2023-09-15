import enum


class BinaryEndian(enum.Enum):
    Little = 0
    Big = 1


def utf8_string_length(string: str) -> int:
    return len(string.encode('utf-8'))
