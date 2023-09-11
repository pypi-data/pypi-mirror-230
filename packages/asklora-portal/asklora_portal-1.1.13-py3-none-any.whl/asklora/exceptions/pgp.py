from asklora.exceptions import ExceptionWithMessage


class PGPError(ExceptionWithMessage):
    message = "PGP error"


class KeysError(PGPError):
    message = "Key error, please check"


class DecryptionError(PGPError):
    message = "Cannot decrypt the message"


class EncryptionError(PGPError):
    message = "Cannot encrypt the message"
