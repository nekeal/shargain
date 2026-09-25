from unittest.mock import Mock, patch

import pytest
from telebot.types import Chat, Message, User

from shargain.offers.models import OfferLike
from shargain.offers.tests.factories import OfferFactory
from shargain.telegram.bot import TelegramBot, handle_like_reply, is_like_reply

pytestmark = pytest.mark.django_db


@pytest.fixture
def mock_reply_message():
    def _create_message(text, reply_text=None):
        msg = Mock(spec=Message)
        msg.text = text
        msg.from_user = User(id=789, is_bot=False, first_name="Test", username="testuser")
        msg.chat = Chat(id=456, type="private")

        if reply_text:
            reply_msg = Mock(spec=Message)
            reply_msg.text = reply_text
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
    assert is_like_reply(mock_reply_message("random", "reply text")) is False
    assert is_like_reply(mock_reply_message("like", None)) is False


@patch.object(TelegramBot.get_bot(), "reply_to")
def test_handle_like_reply_adds_like(mock_reply_to, mock_reply_message):
    offer = OfferFactory(url="https://olx.pl/offer123")
    msg = mock_reply_message(text="like", reply_text=f"Check this out: {offer.url}")

    handle_like_reply(msg)

    assert OfferLike.objects.count() == 1
    like = OfferLike.objects.first()
    assert like.offer == offer
    assert like.liker_label == "testuser (Test)"
    mock_reply_to.assert_called_once()
    assert "Liked 1 offer" in mock_reply_to.call_args[0][1]


@patch.object(TelegramBot.get_bot(), "reply_to")
def test_handle_like_reply_removes_like_on_unlike(mock_reply_to, mock_reply_message):
    offer = OfferFactory(url="https://olx.pl/offer123")
    OfferLike.objects.create(offer=offer, liker_label="testuser (Test)")

    msg = mock_reply_message(text="unlike", reply_text=f"Check this out: {offer.url}")
    handle_like_reply(msg)

    assert OfferLike.objects.count() == 0
    mock_reply_to.assert_called_once()
    assert "Unliked 1 offer" in mock_reply_to.call_args[0][1]


@patch.object(TelegramBot.get_bot(), "reply_to")
def test_handle_like_reply_toggles_like(mock_reply_to, mock_reply_message):
    offer = OfferFactory(url="https://olx.pl/offer123")
    OfferLike.objects.create(offer=offer, liker_label="testuser (Test)")

    msg = mock_reply_message(text="like", reply_text=f"Check this out: {offer.url}")
    handle_like_reply(msg)

    assert OfferLike.objects.count() == 0
    mock_reply_to.assert_called_once()
    assert "Unliked 1 offer" in mock_reply_to.call_args[0][1]


@patch.object(TelegramBot.get_bot(), "reply_to")
def test_handle_like_reply_no_offers(mock_reply_to, mock_reply_message):
    msg = mock_reply_message(text="like", reply_text="Just some text with no urls")
    handle_like_reply(msg)

    assert OfferLike.objects.count() == 0
    mock_reply_to.assert_called_once()
    assert "No offers found" in mock_reply_to.call_args[0][1]


@patch.object(TelegramBot.get_bot(), "reply_to")
def test_handle_liked_command_no_likes(mock_reply_to, mock_reply_message):
    msg = mock_reply_message(text="/liked")
    from shargain.telegram.bot import handle_liked_command

    handle_liked_command(msg)
    mock_reply_to.assert_called_once()
    assert "You haven't liked any offers yet" in mock_reply_to.call_args[0][1]


@patch.object(TelegramBot.get_bot(), "reply_to")
def test_handle_liked_command_with_likes(mock_reply_to, mock_reply_message):
    offer1 = OfferFactory(url="https://olx.pl/offer1", title="Offer 1")
    offer2 = OfferFactory(url="https://olx.pl/offer2", title="Offer 2")
    OfferLike.objects.create(offer=offer1, liker_label="testuser (Test)")
    OfferLike.objects.create(offer=offer2, liker_label="testuser (Test)")

    msg = mock_reply_message(text="/liked")
    from shargain.telegram.bot import handle_liked_command

    handle_liked_command(msg)
    mock_reply_to.assert_called_once()
    response_text = mock_reply_to.call_args[0][1]
    assert "Your latest liked offers:" in response_text
    assert "Offer 1" in response_text
    assert "Offer 2" in response_text
