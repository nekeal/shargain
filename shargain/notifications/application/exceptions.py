from shargain.commons.application.exceptions import ApplicationException


class NotificationConfigDoesNotExist(ApplicationException):
    """Raised when a notification config does not exist."""

    code: str = "notification_config_does_not_exist"
    message: str = "Notification config does not exist."
