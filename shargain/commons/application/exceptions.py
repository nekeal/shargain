class ApplicationException(Exception):
    """
    Base exception for application layer errors.
    Subclasses must override 'code' and 'message' class attributes.
    """

    code: str = "application_error"
    message: str = "An application error occurred."

    def __init__(self):
        super().__init__(self.message)
