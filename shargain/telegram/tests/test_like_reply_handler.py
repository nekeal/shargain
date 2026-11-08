from unittest.mock import Mock, patch

import pytest
from django.utils import timezone
from telebot.types import Chat, Message, User

from shargain.accounts.tests.factories import UserFactory
from shargain.notifications.tests.factories import NotificationConfigFactory
from shargain.offers.models import UserOfferState
from shargain.offers.tests.factories import OfferFactory, ScrappingTargetFactory
from shargain.telegram.bot import TelegramBot, handle_like_reply, is_like_reply

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
def mock_reply_message(chat_id):
    def _create_message(text, reply_text=None, chat_id_override=None):
        cid = chat_id_override if chat_id_override is not None else chat_id
        msg = Mock(spec=Message)
        msg.text = text
        msg.from_user = User(id=789, is_bot=False, first_name="Test", username="testuser")
        msg.chat = Chat(id=cid, type="private")

        if reply_text:
            reply_msg = Mock(spec=Message)
            reply_msg.text = reply_text
            reply_msg.chat = msg.chat
            msg.reply_to_message = reply_msg
        else:
            msg.reply_to_message = None

        return msg

    return _create_message


def test_is_like_reply(mock_reply_message):
    assert is_like_reply(mock_reply_message("like", "reply text")) is True
    assert is_like_reply(mock_reply_message("❤️", "reply text")) is True
    assert is_like_reply(mock_reply_message("👍", "reply text")) is True
    assert is_like_reply(mock_reply_message("unlike", "reply text")) is True
    assert is_like_reply(mock_reply_message("💔", "reply text")) is True
    assert is_like_reply(mock_reply_message("👎", "reply text")) is True
    assert is_like_reply(mock_reply_message("random", "reply text")) is False
    assert is_like_reply(mock_reply_message("like", None)) is False


@patch.object(TelegramBot.get_bot(), "reply_to")
def test_handle_like_reply_adds_like(mock_reply_to, mock_reply_message, user, target):
    offer = OfferFactory(url="https://olx.pl/offer123", target=target)
    msg = mock_reply_message(text="like", reply_text=f"Check this out: {offer.url}")

    handle_like_reply(msg)

    state = UserOfferState.objects.filter(user=user, offer=offer).first()
    assert state is not None
    assert state.liked_at is not None
    mock_reply_to.assert_called_once()
    assert "Liked 1 offer" in mock_reply_to.call_args[0][1]


@patch.object(TelegramBot.get_bot(), "reply_to")
def test_handle_like_reply_removes_like_on_unlike(mock_reply_to, mock_reply_message, user, target):
    offer = OfferFactory(url="https://olx.pl/offer123", target=target)
    UserOfferState.objects.create(user=user, offer=offer, liked_at=timezone.now())

    msg = mock_reply_message(text="unlike", reply_text=f"Check this out: {offer.url}")
    handle_like_reply(msg)

    assert not UserOfferState.objects.filter(user=user, offer=offer, liked_at__isnull=False).exists()
    mock_reply_to.assert_called_once()
    assert "Unliked 1 offer" in mock_reply_to.call_args[0][1]


@patch.object(TelegramBot.get_bot(), "reply_to")
def test_handle_like_reply_toggles_like(mock_reply_to, mock_reply_message, user, target):
    offer = OfferFactory(url="https://olx.pl/offer123", target=target)
    UserOfferState.objects.create(user=user, offer=offer, liked_at=timezone.now())

    msg = mock_reply_message(text="like", reply_text=f"Check this out: {offer.url}")
    handle_like_reply(msg)

    assert not UserOfferState.objects.filter(user=user, offer=offer, liked_at__isnull=False).exists()
    mock_reply_to.assert_called_once()
    assert "Unliked 1 offer" in mock_reply_to.call_args[0][1]


@patch.object(TelegramBot.get_bot(), "reply_to")
def test_handle_like_reply_toggles_multiple_offers_when_all_liked(mock_reply_to, mock_reply_message, user, target):
    offer1 = OfferFactory(url="https://olx.pl/offer1", target=target)
    offer2 = OfferFactory(url="https://olx.pl/offer2", target=target)
    UserOfferState.objects.create(user=user, offer=offer1, liked_at=timezone.now())
    UserOfferState.objects.create(user=user, offer=offer2, liked_at=timezone.now())

    msg = mock_reply_message(text="❤️", reply_text=f"Offers: {offer1.url} and {offer2.url}")
    handle_like_reply(msg)

    assert not UserOfferState.objects.filter(user=user, offer__in=[offer1, offer2], liked_at__isnull=False).exists()
    mock_reply_to.assert_called_once()
    assert "Unliked 2 offer" in mock_reply_to.call_args[0][1]


@patch.object(TelegramBot.get_bot(), "reply_to")
def test_handle_like_reply_likes_all_when_some_not_liked(mock_reply_to, mock_reply_message, user, target):
    offer1 = OfferFactory(url="https://olx.pl/offer1", target=target)
    offer2 = OfferFactory(url="https://olx.pl/offer2", target=target)
    UserOfferState.objects.create(user=user, offer=offer1, liked_at=timezone.now())

    msg = mock_reply_message(text="❤️", reply_text=f"Offers: {offer1.url} and {offer2.url}")
    handle_like_reply(msg)

    assert UserOfferState.objects.filter(user=user, offer=offer1, liked_at__isnull=False).exists()
    assert UserOfferState.objects.filter(user=user, offer=offer2, liked_at__isnull=False).exists()
    mock_reply_to.assert_called_once()
    assert "Liked 2 offer" in mock_reply_to.call_args[0][1]


@patch.object(TelegramBot.get_bot(), "reply_to")
def test_handle_like_reply_no_offers(mock_reply_to, mock_reply_message):
    msg = mock_reply_message(text="like", reply_text="Just some text with no urls")
    handle_like_reply(msg)

    assert UserOfferState.objects.count() == 0
    mock_reply_to.assert_called_once()
    assert "No offers found" in mock_reply_to.call_args[0][1]


@patch.object(TelegramBot.get_bot(), "reply_to")
def test_handle_like_reply_rejection_when_chat_has_no_owner(mock_reply_to, mock_reply_message, chat_id):
    config_no_owner = NotificationConfigFactory(owner=None, chatid=str(chat_id))
    target_no_owner = ScrappingTargetFactory(owner=None, notification_config=config_no_owner)
    offer = OfferFactory(url="https://olx.pl/offer-no-owner", target=target_no_owner)

    msg = mock_reply_message(text="like", reply_text=f"Check: {offer.url}")
    handle_like_reply(msg)

    mock_reply_to.assert_called_once()
    assert "No offers found" in mock_reply_to.call_args[0][1]


@patch.object(TelegramBot.get_bot(), "reply_to")
def test_handle_like_reply_rejection_mismatched_chat_id(mock_reply_to, mock_reply_message, user):
    other_config = NotificationConfigFactory(owner=user, chatid="999")
    other_target = ScrappingTargetFactory(owner=user, notification_config=other_config)
    offer = OfferFactory(url="https://olx.pl/offer-mismatch", target=other_target)

    # Message is sent in chat 456, but offer belongs to chat 999
    msg = mock_reply_message(text="like", reply_text=f"Check: {offer.url}", chat_id_override=456)
    handle_like_reply(msg)

    mock_reply_to.assert_called_once()
    assert "No offers found" in mock_reply_to.call_args[0][1]


@patch.object(TelegramBot.get_bot(), "reply_to")
def test_offer_from_another_user_target_with_same_url_excluded(
    mock_reply_to, mock_reply_message, user, target, chat_id
):
    other_user = UserFactory()
    other_config = NotificationConfigFactory(owner=other_user, chatid="888")
    other_target = ScrappingTargetFactory(owner=other_user, notification_config=other_config)

    url = "https://olx.pl/duplicate-url"
    offer1 = OfferFactory(url=url, target=target)
    offer2 = OfferFactory(url=url, target=other_target)

    msg = mock_reply_message(text="like", reply_text=f"Check: {url}", chat_id_override=chat_id)
    handle_like_reply(msg)

    assert UserOfferState.objects.filter(user=user, offer=offer1, liked_at__isnull=False).exists()
    assert not UserOfferState.objects.filter(user=other_user, offer=offer2).exists()
    mock_reply_to.assert_called_once()
    assert "Liked 1 offer" in mock_reply_to.call_args[0][1]
