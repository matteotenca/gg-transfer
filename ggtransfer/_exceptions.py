class GgTransferError(Exception):

    msg: str
    _PREFIX: str

    def __init__(self, message: str):
        self._PREFIX = "\n *** ERROR: "
        self.msg = self._PREFIX + message


class GgIOError(GgTransferError):

    _PREFIX: str = "I/O - "

    def __init__(self, message: str):
        super().__init__(self._PREFIX + message)


class GgUnicodeError(GgTransferError):

    _PREFIX: str = "Data type mismatch - "

    def __init__(self, message: str):
        super().__init__(self._PREFIX + message)
