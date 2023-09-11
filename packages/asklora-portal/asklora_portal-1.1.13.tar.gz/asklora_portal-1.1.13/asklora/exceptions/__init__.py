class ExceptionWithMessage(Exception):
    message: str = "Exception raised"

    def __init__(self, message: str | None = None) -> None:
        if message:
            self.message = message

        super().__init__(self.message)
