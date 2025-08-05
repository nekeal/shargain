from django.http import HttpRequest
from ninja import NinjaAPI, Schema
from ninja.errors import HttpError

from shargain.offers.application.actor import Actor
from shargain.offers.application.commands.add_scraping_url import add_scraping_url
from shargain.offers.application.commands.change_notification_config import change_notification_config
from shargain.offers.application.commands.delete_scraping_url import delete_scraping_url
from shargain.offers.application.commands.set_scraping_url_active_status import set_scraping_url_active_status
from shargain.offers.application.commands.toggle_target_notifications import toggle_target_notifications
from shargain.offers.application.exceptions import (
    NotificationConfigDoesNotExist,
    ScrapingUrlDoesNotExist,
    TargetDoesNotExist,
)
from shargain.offers.application.queries.get_target import get_target, get_target_by_user

router = NinjaAPI()


class ErrorSchema(Schema):
    detail: str


class NotificationConfigRequest(Schema):
    notification_config_id: int | None = None


class TargetWithConfigResponse(Schema):
    id: int
    name: str
    is_active: bool
    enable_notifications: bool
    notification_config_id: int | None


class AddUrlRequest(Schema):
    url: str


class ScrapingUrlResponse(Schema):
    id: int
    url: str
    name: str


class TargetResponse(Schema):
    id: int
    name: str
    enable_notifications: bool
    is_active: bool
    urls: list[ScrapingUrlResponse]


class ToggleNotificationsRequest(Schema):
    enable: bool | None = None


class ToggleNotificationsResponse(Schema):
    enable_notifications: bool


def get_actor(request: HttpRequest) -> Actor:
    if not request.user or not request.user.id:
        raise HttpError(401, "Authentication required")
    return Actor(user_id=request.user.id)


@router.get("/targets/my-target", response={200: TargetResponse, 404: ErrorSchema})
def get_my_target(request: HttpRequest):
    actor = get_actor(request)
    try:
        return get_target_by_user(actor)
    except TargetDoesNotExist as e:
        raise HttpError(404, "Target not found") from e


@router.get("/targets/{target_id}", response={200: TargetResponse, 404: ErrorSchema})
def get_single_target(request: HttpRequest, target_id: int):
    actor = get_actor(request)
    try:
        return get_target(actor, target_id)
    except TargetDoesNotExist as e:
        raise HttpError(404, "Target not found") from e


@router.post("/targets/{target_id}/notification-config", response={200: TargetWithConfigResponse, 404: ErrorSchema})
def update_notification_config(request: HttpRequest, target_id: int, payload: NotificationConfigRequest):
    actor = get_actor(request)
    try:
        return change_notification_config(actor, target_id, payload.notification_config_id)
    except TargetDoesNotExist as e:
        raise HttpError(404, "Target not found") from e
    except NotificationConfigDoesNotExist as e:
        raise HttpError(404, "Notification config not found") from e


@router.post("/targets/{target_id}/add-url", response={200: ScrapingUrlResponse, 404: ErrorSchema})
def add_url_to_target(request: HttpRequest, target_id: int, payload: AddUrlRequest):
    actor = get_actor(request)
    try:
        return add_scraping_url(actor, payload.url, target_id)
    except TargetDoesNotExist as e:
        raise HttpError(404, "Target not found") from e


@router.delete("/targets/{target_id}/urls/{url_id}", response={204: None, 404: ErrorSchema})
def delete_target_url(request: HttpRequest, target_id: int, url_id: int):
    actor = get_actor(request)
    delete_scraping_url(actor, url_id)
    return 204, None


@router.post("/targets/{target_id}/urls/{url_id}/activate", response={200: ScrapingUrlResponse, 404: ErrorSchema})
def activate_scraping_url(request: HttpRequest, target_id: int, url_id: int):
    actor = get_actor(request)
    try:
        return set_scraping_url_active_status(actor, url_id, target_id, is_active=True)
    except ScrapingUrlDoesNotExist as e:
        raise HttpError(404, "Scraping url not found") from e


@router.post("/targets/{target_id}/urls/{url_id}/deactivate", response={200: ScrapingUrlResponse, 404: ErrorSchema})
def deactivate_scraping_url(request: HttpRequest, target_id: int, url_id: int):
    actor = get_actor(request)
    try:
        return set_scraping_url_active_status(actor, url_id, target_id, is_active=False)
    except ScrapingUrlDoesNotExist as e:
        raise HttpError(404, "Scraping url not found") from e


@router.post("/targets/{target_id}/toggle-notifications", response={200: ToggleNotificationsResponse, 404: ErrorSchema})
def toggle_notifications(request: HttpRequest, target_id: int, payload: ToggleNotificationsRequest):
    actor = get_actor(request)
    try:
        result = toggle_target_notifications(actor, target_id, payload.enable)
        return ToggleNotificationsResponse(enable_notifications=result.enable_notifications)
    except TargetDoesNotExist as e:
        raise HttpError(404, "Target not found") from e
