from django.http import HttpRequest
from ninja import NinjaAPI, Schema
from ninja.errors import HttpError
from pydantic.alias_generators import to_camel
from pydantic.networks import HttpUrl

from shargain.commons.application.actor import Actor
from shargain.notifications.application.commands.create_notification_config import (
    create_notification_config,
)
from shargain.notifications.application.commands.delete_notification_config import (
    delete_notification_config,
)
from shargain.notifications.application.commands.update_notification_config import (
    update_notification_config,
)
from shargain.notifications.application.exceptions import NotificationConfigDoesNotExist
from shargain.notifications.application.queries.get_notification_config import (
    get_notification_config,
)
from shargain.notifications.application.queries.list_notification_configs import (
    list_notification_configs,
)
from shargain.notifications.models import NotificationChannelChoices
from shargain.offers.application.commands.add_scraping_url import add_scraping_url
from shargain.offers.application.commands.change_notification_config import (
    change_notification_config,
)
from shargain.offers.application.commands.delete_scraping_url import delete_scraping_url
from shargain.offers.application.commands.send_test_notification import (
    send_test_notification,
)
from shargain.offers.application.commands.set_scraping_url_active_status import (
    set_scraping_url_active_status,
)
from shargain.offers.application.commands.toggle_target_notifications import (
    toggle_target_notifications,
)
from shargain.offers.application.commands.update_scraping_target_name import (
    update_scraping_target_name,
)
from shargain.offers.application.exceptions import (
    ApplicationException,
    ScrapingUrlDoesNotExist,
    TargetDoesNotExist,
)
from shargain.offers.application.queries.get_target import (
    get_target,
    get_target_by_user,
)
from shargain.telegram.application.commands.generate_telegram_token import (
    UserDoesNotExist,
    generate_telegram_token,
)
from shargain.telegram.bot import TelegramBot

# Import the auth router
from .auth import auth_router
from .auth import router as protected_router

router = NinjaAPI(csrf=True)

# Include both routers
router.add_router("/auth", auth_router)
router.add_router("/", protected_router)


class ErrorSchema(Schema):
    detail: str


class BaseSchema(Schema):
    class Config:
        alias_generator = to_camel
        populate_by_name = True


class NotificationConfigRequest(BaseSchema):
    notification_config_id: int | None = None


class NotificationConfigResponse(BaseSchema):
    id: int
    name: str | None
    channel: str
    chat_id: str


class NotificationConfigListResponse(BaseSchema):
    configs: list[NotificationConfigResponse]


class CreateNotificationConfigRequest(BaseSchema):
    name: str | None = None
    chat_id: str
    channel: NotificationChannelChoices = NotificationChannelChoices.TELEGRAM


class UpdateNotificationConfigRequest(BaseSchema):
    name: str | None


class TargetWithConfigResponse(BaseSchema):
    id: int
    name: str
    is_active: bool
    enable_notifications: bool
    notification_config_id: int | None


class ScrapingUrlResponse(BaseSchema):
    id: int
    url: str
    name: str
    is_active: bool
    last_checked_at: str | None = None


class TargetResponse(BaseSchema):
    id: int
    name: str
    enable_notifications: bool
    notification_config_id: int | None
    is_active: bool
    urls: list[ScrapingUrlResponse]


class ToggleNotificationsRequest(BaseSchema):
    enable: bool | None = None


class ToggleNotificationsResponse(BaseSchema):
    enable_notifications: bool


class GenerateTokenResponse(BaseSchema):
    telegram_bot_url: str


class VerifyTokenRequest(BaseSchema):
    token: str
    chat_id: int


class VerifyTokenResponse(BaseSchema):
    success: bool


def get_actor(request: HttpRequest) -> Actor:
    if not request.user or not request.user.id:
        raise HttpError(401, "Authentication required")
    return Actor(user_id=request.user.id)


@router.get(
    "/targets/my-target",
    operation_id="get_my_target",
    by_alias=True,
    response={200: TargetResponse, 404: ErrorSchema},
)
def get_my_target(request: HttpRequest):
    actor = get_actor(request)
    try:
        return get_target_by_user(actor)
    except TargetDoesNotExist as e:
        raise HttpError(404, "Target not found") from e


@router.get(
    "/targets/{target_id}",
    operation_id="get_single_target",
    by_alias=True,
    response={200: TargetResponse, 404: ErrorSchema},
)
def get_single_target(request: HttpRequest, target_id: int):
    actor = get_actor(request)
    try:
        return get_target(actor, target_id)
    except TargetDoesNotExist as e:
        raise HttpError(404, "Target not found") from e


@router.post(
    "/targets/{target_id}/notification-config",
    operation_id="update_target_notification_config",
    by_alias=True,
    response={200: TargetWithConfigResponse, 404: ErrorSchema},
)
def update_scraping_target_notification_config(
    request: HttpRequest, target_id: int, payload: NotificationConfigRequest
):
    actor = get_actor(request)
    try:
        return change_notification_config(actor, target_id, payload.notification_config_id)
    except TargetDoesNotExist as e:
        raise HttpError(404, "Target not found") from e
    except NotificationConfigDoesNotExist as e:
        raise HttpError(404, "Notification config not found") from e


class AddUrlRequest(BaseSchema):
    url: HttpUrl
    name: str | None = None


@router.post(
    "/targets/{target_id}/add-url",
    operation_id="add_url_to_target",
    by_alias=True,
    response={200: ScrapingUrlResponse, 404: ErrorSchema},
)
def add_url_to_target(request: HttpRequest, target_id: int, payload: AddUrlRequest):
    actor = get_actor(request)
    try:
        return add_scraping_url(actor, str(payload.url), target_id, name=payload.name)
    except TargetDoesNotExist as e:
        raise HttpError(404, "Target not found") from e


@router.delete(
    "/targets/{target_id}/urls/{url_id}",
    operation_id="delete_target_url",
    by_alias=True,
    response={204: None, 404: ErrorSchema},
)
def delete_target_url(request: HttpRequest, target_id: int, url_id: int):
    actor = get_actor(request)
    delete_scraping_url(actor, url_id)
    return 204, None


@router.post(
    "/targets/{target_id}/urls/{url_id}/activate",
    operation_id="activate_scraping_url",
    by_alias=True,
    response={200: ScrapingUrlResponse, 404: ErrorSchema},
)
def activate_scraping_url(request: HttpRequest, target_id: int, url_id: int):
    actor = get_actor(request)
    try:
        return set_scraping_url_active_status(actor, url_id, target_id, is_active=True)
    except ScrapingUrlDoesNotExist as e:
        raise HttpError(404, "Scraping url not found") from e


@router.post(
    "/targets/{target_id}/urls/{url_id}/deactivate",
    operation_id="deactivate_scraping_url",
    by_alias=True,
    response={200: ScrapingUrlResponse, 404: ErrorSchema},
)
def deactivate_scraping_url(request: HttpRequest, target_id: int, url_id: int):
    actor = get_actor(request)
    try:
        return set_scraping_url_active_status(actor, url_id, target_id, is_active=False)
    except ScrapingUrlDoesNotExist as e:
        raise HttpError(404, "Scraping url not found") from e


@router.post(
    "/targets/{target_id}/toggle-notifications",
    operation_id="toggle_target_notifications",
    by_alias=True,
    response={200: ToggleNotificationsResponse, 404: ErrorSchema},
)
def toggle_notifications(request: HttpRequest, target_id: int, payload: ToggleNotificationsRequest):
    actor = get_actor(request)
    try:
        result = toggle_target_notifications(actor, target_id, payload.enable)
        return ToggleNotificationsResponse(enable_notifications=result.enable_notifications)
    except TargetDoesNotExist as e:
        raise HttpError(404, "Target not found") from e


@router.post(
    "/targets/{target_id}/send-test-notification",
    operation_id="send_target_test_notification",
    by_alias=True,
    response={204: None, 404: ErrorSchema, 400: ErrorSchema},
)
def send_test_notification_endpoint(request: HttpRequest, target_id: int):
    actor = get_actor(request)
    try:
        send_test_notification(actor, target_id)
        return 204, None
    except TargetDoesNotExist as e:
        raise HttpError(404, "Target not found") from e
    except NotificationConfigDoesNotExist as e:
        raise HttpError(400, "Notification config not found") from e


class UpdateTargetNameRequest(BaseSchema):
    name: str


@router.patch(
    "/targets/{target_id}/update-name",
    operation_id="update_target_name",
    by_alias=True,
    response={204: None, 404: ErrorSchema, 400: ErrorSchema},
)
def update_target_name(request: HttpRequest, target_id: int, payload: UpdateTargetNameRequest):
    actor = get_actor(request)
    try:
        update_scraping_target_name(actor=actor, target_id=target_id, name=payload.name)
        return 204, None
    except TargetDoesNotExist as e:
        raise HttpError(404, "Target not found") from e
    except ValueError as e:
        raise HttpError(400, str(e)) from e


@router.post(
    "/notifications/telegram/generate-token",
    operation_id="generate_telegram_token",
    by_alias=True,
    response={
        200: GenerateTokenResponse,
        404: ErrorSchema,
    },
)
def generate_telegram_token_endpoint(request: HttpRequest):
    try:
        actor = get_actor(request)
        result = generate_telegram_token(TelegramBot(), actor=actor)
        return GenerateTokenResponse(telegram_bot_url=result.telegram_bot_url)
    except UserDoesNotExist:
        raise HttpError(404, "User not found") from None
    except ApplicationException as e:
        raise HttpError(400, str(e)) from e


@router.post(
    "/notifications",
    operation_id="create_notification_config",
    by_alias=True,
    response={200: NotificationConfigResponse, 400: ErrorSchema},
)
def create_notification_config_endpoint(request: HttpRequest, payload: CreateNotificationConfigRequest):
    actor = get_actor(request)
    try:
        result = create_notification_config(
            actor=actor,
            name=payload.name,
            chat_id=payload.chat_id,
            channel=payload.channel,
        )
        return result
    except ValueError as e:
        raise HttpError(400, str(e)) from e


@router.put(
    "/notifications/{config_id}",
    operation_id="update_notification_config",
    by_alias=True,
    response={200: NotificationConfigResponse, 404: ErrorSchema},
)
def update_notification_config_endpoint(request: HttpRequest, config_id: int, payload: UpdateNotificationConfigRequest):
    actor = get_actor(request)
    try:
        result = update_notification_config(
            actor=actor,
            config_id=config_id,
            name=payload.name,
        )
        return result
    except NotificationConfigDoesNotExist as e:
        raise HttpError(404, "Notification config not found") from e


@router.delete(
    "/notifications/{config_id}",
    operation_id="delete_notification_config",
    by_alias=True,
    response={204: None, 404: ErrorSchema},
)
def delete_notification_config_endpoint(request: HttpRequest, config_id: int):
    actor = get_actor(request)
    try:
        delete_notification_config(actor=actor, config_id=config_id)
        return 204, None
    except NotificationConfigDoesNotExist as e:
        raise HttpError(404, "Notification config not found") from e


@router.get(
    "/notifications/{config_id}",
    operation_id="get_notification_config",
    by_alias=True,
    response={200: NotificationConfigResponse, 404: ErrorSchema},
)
def get_notification_config_endpoint(request: HttpRequest, config_id: int):
    actor = get_actor(request)
    try:
        result = get_notification_config(actor=actor, config_id=config_id)
        return result
    except NotificationConfigDoesNotExist as e:
        raise HttpError(404, "Notification config not found") from e


@router.get(
    "/notifications",
    operation_id="list_notification_configs",
    by_alias=True,
    response={200: NotificationConfigListResponse},
)
def list_notification_configs_endpoint(request: HttpRequest):
    actor = get_actor(request)
    result = list_notification_configs(actor=actor)
    return result
