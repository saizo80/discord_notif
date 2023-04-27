class SendError(Exception):
    """Raised when there is an error sending a message to discord webhook"""

    def __init__(self, message: str = None, code: int = None) -> None:
        self.message = message
        self.code = code
        super().__init__(self.message)
