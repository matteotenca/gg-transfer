"""
        gg-transfer - a tool to transfer files encoded in audio via FSK modulation
        Copyright (C) 2024 Matteo Tenca

        This program is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


class GgTransferError(Exception):
    msg: str
    _PREFIX: str

    def __init__(self, message: str):
        self._PREFIX = "*** ERROR: "
        self.msg = self._PREFIX + message

    def __str__(self) -> str:
        return self.msg


class GgIOError(GgTransferError):
    _PREFIX: str = "I/O - "

    def __init__(self, message: str):
        super().__init__(self._PREFIX + message)


class GgUnicodeError(GgTransferError):
    _PREFIX: str = "Data type mismatch - "

    def __init__(self, message: str):
        super().__init__(self._PREFIX + message)


class GgArgumentsError(GgTransferError):
    _PREFIX: str = "Invalid arguments - "

    def __init__(self, message: str):
        super().__init__(self._PREFIX + message)


class GgChecksumError(GgTransferError):
    _PREFIX: str = "Checksum error - "

    def __init__(self, message: str):
        super().__init__(self._PREFIX + message)
