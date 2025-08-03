# shargain/offers/application/exceptions.py


class ApplicationException(Exception):
    """
    Base exception for application layer errors.
    Subclasses must override 'code' and 'message' class attributes.
    """

    code: str = "application_error"
    message: str = "An application error occurred."

    def __init__(self):
        super().__init__(self.message)


class TargetDoesNotExist(ApplicationException):
    """Raised when a target does not exist."""

    code: str = "target_does_not_exist"
    message: str = "Target does not exist."


class NotificationConfigDoesNotExist(ApplicationException):
    """Raised when a notification config does not exist."""

    code: str = "notification_config_does_not_exist"
    message: str = "Notification config does not exist."


class ScrapingUrlDoesNotExist(ApplicationException):
    """Raised when a scraping url does not exist."""

    code: str = "scraping_url_does_not_exist"
    message: str = "Scraping URL does not exist."
