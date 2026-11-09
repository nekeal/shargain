from unittest.mock import Mock, patch

import pytest
from django.utils import timezone
from telebot.types import Chat, Message, User

from shargain.accounts.tests.factories import UserFactory
from shargain.notifications.tests.factories import NotificationConfigFactory
from shargain.offers.models import UserOfferState
from shargain.offers.tests.factories import OfferFactory, ScrappingTargetFactory
from shargain.telegram.bot import (
    TelegramBot,
    handle_liked_command,
    handle_unlike_by_id_command,
    resolve_user_for_chat,
    resolve_user_for_offer_chat,
)

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def chat_id():
    return 456


@pytest.fixture
def notification_config(user, chat_id):
    return NotificationConfigFactory(owner=user, chatid=str(chat_id))


@pytest.fixture
def target(user, notification_config):
    return ScrappingTargetFactory(owner=user, notification_config=notification_config)


@pytest.fixture
def mock_message(chat_id):
    def _create_message(text, chat_id_override=None):
        cid = chat_id_override if chat_id_override is not None else chat_id
        msg = Mock(spec=Message)
        msg.text = text
        msg.from_user = User(id=789, is_bot=False, first_name="Test", username="testuser")
        msg.chat = Chat(id=cid, type="private")
        return msg

    return _create_message


def test_resolve_user_for_offer_chat(user, target, chat_id):
    offer = OfferFactory(target=target)
    assert resolve_user_for_offer_chat(offer, chat_id) == user.id
    assert resolve_user_for_offer_chat(offer, str(chat_id)) == user.id
    assert resolve_user_for_offer_chat(offer, 99999) is None

    # Target without notification_config
    target_no_config = ScrappingTargetFactory(notification_config=None)
    offer_no_config = OfferFactory(target=target_no_config)
    assert resolve_user_for_offer_chat(offer_no_config, chat_id) is None

    # Config without owner
    config_no_owner = NotificationConfigFactory(owner=None, chatid=str(chat_id))
    target_no_owner = ScrappingTargetFactory(owner=None, notification_config=config_no_owner)
    offer_no_owner = OfferFactory(target=target_no_owner)
    assert resolve_user_for_offer_chat(offer_no_owner, chat_id) is None


def test_resolve_user_for_chat_single_owner(user, target, chat_id):
    assert resolve_user_for_chat(chat_id) == user.id
    assert resolve_user_for_chat(str(chat_id)) == user.id


def test_resolve_user_for_chat_multiple_targets_same_owner(user, notification_config, chat_id):
    ScrappingTargetFactory(owner=user, notification_config=notification_config)
    ScrappingTargetFactory(owner=user, notification_config=notification_config)
    assert resolve_user_for_chat(chat_id) == user.id


def test_resolve_user_for_chat_ambiguous_multiple_owners(user, chat_id):
    NotificationConfigFactory(owner=user, chatid=str(chat_id))
    other_user = UserFactory()
    other_config = NotificationConfigFactory(owner=other_user, chatid=str(chat_id))
    ScrappingTargetFactory(owner=other_user, notification_config=other_config)
    ScrappingTargetFactory(owner=user, notification_config=NotificationConfigFactory(owner=user, chatid=str(chat_id)))

    # Two different owners associated with the same chat id
    assert resolve_user_for_chat(chat_id) is None


def test_resolve_user_for_chat_none(chat_id):
    assert resolve_user_for_chat(chat_id) is None


def test_resolve_user_for_chat_no_owner(chat_id):
    config = NotificationConfigFactory(owner=None, chatid=str(chat_id))
    ScrappingTargetFactory(owner=None, notification_config=config)
    assert resolve_user_for_chat(chat_id) is None


@patch.object(TelegramBot.get_bot(), "reply_to")
def test_handle_liked_command_no_user(mock_reply_to, mock_message):
    msg = mock_message(text="/liked", chat_id_override=123456)
    handle_liked_command(msg)

    mock_reply_to.assert_called_once()
    assert "Could not find registered targets for this chat" in mock_reply_to.call_args[0][1]


@patch.object(TelegramBot.get_bot(), "reply_to")
def test_handle_liked_command_no_likes(mock_reply_to, mock_message, target, chat_id):
    msg = mock_message(text="/liked", chat_id_override=chat_id)
    handle_liked_command(msg)

    mock_reply_to.assert_called_once()
    assert "No offers have been liked in this chat yet!" in mock_reply_to.call_args[0][1]


@patch.object(TelegramBot.get_bot(), "reply_to")
def test_handle_liked_command_with_likes(mock_reply_to, mock_message, user, target, chat_id):
    offer1 = OfferFactory(url="https://olx.pl/offer1", title="Offer 1", target=target)
    offer2 = OfferFactory(url="https://olx.pl/offer2", title="Offer 2", target=target)
    UserOfferState.objects.create(user=user, offer=offer1, liked_at=timezone.now())
    UserOfferState.objects.create(user=user, offer=offer2, liked_at=timezone.now())

    # An offer from another chat/target shouldn't appear
    other_config = NotificationConfigFactory(owner=user, chatid="9999")
    other_target = ScrappingTargetFactory(owner=user, notification_config=other_config)
    other_offer = OfferFactory(url="https://olx.pl/other", title="Other Offer", target=other_target)
    UserOfferState.objects.create(user=user, offer=other_offer, liked_at=timezone.now())

    msg = mock_message(text="/liked", chat_id_override=chat_id)
    handle_liked_command(msg)

    mock_reply_to.assert_called_once()
    response_text = mock_reply_to.call_args[0][1]
    assert "Latest liked offers in this chat:" in response_text
    assert f"• <a href='{offer1.url}'>Offer 1</a> — /unlike_{offer1.id}" in response_text
    assert f"• <a href='{offer2.url}'>Offer 2</a> — /unlike_{offer2.id}" in response_text
    assert "Other Offer" not in response_text
    assert mock_reply_to.call_args[1]["parse_mode"] == "HTML"


@patch.object(TelegramBot.get_bot(), "reply_to")
def test_handle_liked_command_chunking(mock_reply_to, mock_message, user, target, chat_id):
    # Create enough offers to exceed 4000 characters
    long_title = "A" * 150
    offers = []
    for i in range(35):
        offer = OfferFactory(url=f"https://olx.pl/long-offer-{i}", title=f"{long_title} {i}", target=target)
        UserOfferState.objects.create(user=user, offer=offer, liked_at=timezone.now())
        offers.append(offer)

    msg = mock_message(text="/liked", chat_id_override=chat_id)
    handle_liked_command(msg)

    assert mock_reply_to.call_count >= 2
    for call in mock_reply_to.call_args_list:
        chunk = call[0][1]
        assert len(chunk) <= 4000
        assert call[1]["parse_mode"] == "HTML"


@patch.object(TelegramBot.get_bot(), "reply_to")
def test_handle_unlike_by_id_command(mock_reply_to, mock_message, user, target, chat_id):
    offer = OfferFactory(url="https://olx.pl/offer1", title="Offer 1", target=target)
    UserOfferState.objects.create(user=user, offer=offer, liked_at=timezone.now())

    msg = mock_message(text=f"/unlike_{offer.id}", chat_id_override=chat_id)
    handle_unlike_by_id_command(msg)

    assert not UserOfferState.objects.filter(user=user, offer=offer, liked_at__isnull=False).exists()
    mock_reply_to.assert_called_once()
    assert "Unliked offer: Offer 1" in mock_reply_to.call_args[0][1]


@patch.object(TelegramBot.get_bot(), "reply_to")
def test_handle_unlike_by_id_command_not_found(mock_reply_to, mock_message, chat_id):
    msg = mock_message(text="/unlike_99999", chat_id_override=chat_id)
    handle_unlike_by_id_command(msg)

    mock_reply_to.assert_called_once()
    assert "Offer not found or not accessible in this chat." in mock_reply_to.call_args[0][1]


@patch.object(TelegramBot.get_bot(), "reply_to")
def test_handle_unlike_by_id_command_with_bot_handle(mock_reply_to, mock_message, user, target, chat_id):
    offer = OfferFactory(url="https://olx.pl/offer1", title="Offer 1", target=target)
    UserOfferState.objects.create(user=user, offer=offer, liked_at=timezone.now())

    msg = mock_message(text=f"/unlike_{offer.id}@shargain_bot", chat_id_override=chat_id)
    handle_unlike_by_id_command(msg)

    assert not UserOfferState.objects.filter(user=user, offer=offer, liked_at__isnull=False).exists()
    mock_reply_to.assert_called_once()
    assert "Unliked offer: Offer 1" in mock_reply_to.call_args[0][1]


@patch.object(TelegramBot.get_bot(), "reply_to")
def test_handle_liked_command_escapes_html(mock_reply_to, mock_message, user, target, chat_id):
    offer = OfferFactory(
        url="https://olx.pl/offer?a=1&b=2",
        title="2 pokoje & balkon <super>",
        target=target,
    )
    UserOfferState.objects.create(user=user, offer=offer, liked_at=timezone.now())

    msg = mock_message(text="/liked", chat_id_override=chat_id)
    handle_liked_command(msg)

    mock_reply_to.assert_called_once()
    text = mock_reply_to.call_args[0][1]
    assert "&amp;" in text
    assert "&lt;super&gt;" in text
    assert "<super>" not in text


@patch.object(TelegramBot.get_bot(), "reply_to")
def test_handle_unlike_by_id_command_different_chat(mock_reply_to, mock_message, user, target, chat_id):
    offer = OfferFactory(url="https://olx.pl/offer1", title="Offer 1", target=target)
    UserOfferState.objects.create(user=user, offer=offer, liked_at=timezone.now())

    # User attempts to unlike from a different chat
    msg = mock_message(text=f"/unlike_{offer.id}", chat_id_override=999)
    handle_unlike_by_id_command(msg)

    # Offer remains liked because it is not accessible from chat 999
    assert UserOfferState.objects.filter(user=user, offer=offer, liked_at__isnull=False).exists()
    mock_reply_to.assert_called_once()
    assert "Offer not found or not accessible in this chat." in mock_reply_to.call_args[0][1]
