from unittest.mock import Mock, patch

import pytest
from telebot.types import Chat, MessageReactionUpdated, ReactionTypeEmoji, User

from shargain.offers.models import OfferLike
from shargain.offers.tests.factories import OfferFactory
from shargain.telegram.bot import TelegramBot, handle_like_reaction

pytestmark = pytest.mark.django_db


@pytest.fixture
def reaction_update():
    def _reaction_update(old_emoji=None, new_emoji=None):
        old_reaction = [ReactionTypeEmoji(type="emoji", emoji=old_emoji)] if old_emoji else []
        new_reaction = [ReactionTypeEmoji(type="emoji", emoji=new_emoji)] if new_emoji else []
        return MessageReactionUpdated(
            message_id=123,
            chat=Chat(id=456, type="private"),
            date=1234567890,
            user=User(id=789, is_bot=False, first_name="Test"),
            actor_chat=None,
            old_reaction=old_reaction,
            new_reaction=new_reaction,
        )

    return _reaction_update


@pytest.fixture
def mock_get_message():
    with patch.object(TelegramBot.get_bot(), "get_message", create=True) as mock:
        yield mock


def test_handle_like_reaction_adds_like(reaction_update, mock_get_message):
    offer = OfferFactory(url="https://olx.pl/offer123")

    mock_message = Mock()
    mock_message.text = f"Check this out: {offer.url}"
    mock_get_message.return_value = mock_message

    update = reaction_update(old_emoji=None, new_emoji="❤️")
    handle_like_reaction(update)

    assert OfferLike.objects.count() == 1
    like = OfferLike.objects.first()
    assert like.offer == offer
    assert like.liker_label == "789"


def test_handle_like_reaction_removes_like(reaction_update, mock_get_message):
    offer = OfferFactory(url="https://olx.pl/offer123")
    OfferLike.objects.create(offer=offer, liker_label="789")

    mock_message = Mock()
    mock_message.text = f"Check this out: {offer.url}"
    mock_get_message.return_value = mock_message

    update = reaction_update(old_emoji="❤️", new_emoji=None)
    handle_like_reaction(update)

    assert OfferLike.objects.count() == 0


def test_handle_like_reaction_ignores_other_emojis(reaction_update, mock_get_message):
    offer = OfferFactory(url="https://olx.pl/offer123")

    mock_message = Mock()
    mock_message.text = f"Check this out: {offer.url}"
    mock_get_message.return_value = mock_message

    update = reaction_update(old_emoji=None, new_emoji="👍")
    handle_like_reaction(update)

    assert OfferLike.objects.count() == 0


def test_handle_like_reaction_no_offers_in_text(reaction_update, mock_get_message):
    mock_message = Mock()
    mock_message.text = "Just some text with no urls"
    mock_get_message.return_value = mock_message

    update = reaction_update(old_emoji=None, new_emoji="❤️")
    handle_like_reaction(update)

    assert OfferLike.objects.count() == 0


def test_handle_like_reaction_idempotent_re_like(reaction_update, mock_get_message):
    offer = OfferFactory(url="https://olx.pl/offer123")
    OfferLike.objects.create(offer=offer, liker_label="789")

    mock_message = Mock()
    mock_message.text = f"Check this out: {offer.url}"
    mock_get_message.return_value = mock_message

    update = reaction_update(old_emoji=None, new_emoji="❤️")
    handle_like_reaction(update)

    assert OfferLike.objects.count() == 1
