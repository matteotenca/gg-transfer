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
