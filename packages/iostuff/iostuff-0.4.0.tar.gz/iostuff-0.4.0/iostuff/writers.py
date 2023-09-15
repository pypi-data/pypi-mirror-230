from io import BytesIO, TextIOWrapper
from .common import BinaryEndian
from typing import Any, Iterable
from struct import pack as pk
from jsonpickle import encode
from _csv import writer


class CSVWriter:
    def __init__(self, file_path: str, file_encoding: str = "utf-8") -> None:
        self.__file_path = file_path
        self.__file_mode = "w"
        self.__file_encoding = file_encoding
        self.__fp = None
        self.__writer = None

    def __enter__(self):
        self.__fp = open(self.__file_path, self.__file_mode,
                         encoding=self.__file_encoding, newline='')
        self.__writer = writer(self.__fp)
        return self

    def __exit__(self, type, value, traceback) -> None:
        self.__fp.close()

    def write_row(self, row: Iterable[Any]) -> None:
        self.__writer.writerow(row)

    def write_rows(self, rows: Iterable[Iterable[Any]]) -> None:
        self.__writer.writerows(rows)


class TextWriter:
    def __init__(self, file_path: str, file_encoding: str = "utf-8") -> None:
        self.__file_path = file_path
        self.__file_mode = "w"
        self.__file_encoding = file_encoding
        self.__fp = None

    def __enter__(self) -> TextIOWrapper:
        self.__fp = open(self.__file_path, self.__file_mode,
                         encoding=self.__file_encoding)
        return self.__fp

    def __exit__(self, type, value, traceback) -> None:
        self.__fp.close()


class JsonWriter:
    def __init__(self, file_path: str, unpickable: bool = True) -> None:
        self.__file_path = file_path
        self.__file_mode = "w"
        self.__file_encoding = "utf-8"
        self.__unpickable = unpickable
        self.__fp = None

    def __enter__(self):
        self.__fp = open(self.__file_path, self.__file_mode,
                         encoding=self.__file_encoding)
        return self

    def __exit__(self, type, value, traceback):
        self.__fp.close()

    def write(self, value: Any) -> None:
        self.__fp.write(encode(value, unpicklable=self.__unpickable))


class MemoryWriter(BytesIO):
    def __init__(self, endian: BinaryEndian = BinaryEndian.Little) -> None:
        self.__endian = "<" if endian == BinaryEndian.Little else ">"

    def __write_num(self, type: str, number: int) -> int:
        return self.write(pk(f"{self.__endian}{type}", number))

    def write_ubyte(self, number: int) -> int:
        return self.__write_num("B", number)

    def write_byte(self, number: int) -> int:
        return self.__write_num("b", number)

    def write_ushort(self, number: int) -> int:
        return self.__write_num("H", number)

    def write_short(self, number: int) -> int:
        return self.__write_num("h", number)

    def write_uint(self, number: int) -> int:
        return self.__write_num("I", number)

    def write_int(self, number: int) -> int:
        return self.__write_num("i", number)

    def write_ulong(self, number: int) -> int:
        return self.__write_num("Q", number)

    def write_long(self, number: int) -> int:
        return self.__write_num("q", number)

    def write_utf8_string(self, string: str) -> int:
        return self.write(string.encode('utf-8'))

    def write_utf8_nt_string(self, string: str, nt: int = 0) -> int:
        return self.write_utf8_string(string) + self.write_ubyte(nt)

    def align(self, number: int) -> int:
        offset = self.tell()
        align = (number - (offset % number)) % number
        return self.seek(offset + align)

    def skip(self, number: int) -> int:
        return self.seek(self.tell() + number)


class BinaryWriter(MemoryWriter):
    def __init__(self, file_path: str, endian: BinaryEndian = BinaryEndian.Little) -> None:
        super().__init__(endian)
        self.__file_path = file_path
        self.__file_mode = "wb"
        self.__fp = None

    def __enter__(self):
        self.__fp = open(self.__file_path, self.__file_mode)
        return self

    def __exit__(self, type, value, traceback):
        self.__fp.write(self.getbuffer())
        self.__fp.close()
