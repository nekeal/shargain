from django.db import migrations

from shargain.offers.migrations.helpers import (
    copy_likes_to_user_offer_states,
    copy_user_offer_states_to_likes,
)


def forwards(apps, schema_editor):
    offer_like_model = apps.get_model("offers", "OfferLike")
    user_offer_state_model = apps.get_model("offers", "UserOfferState")
    copy_likes_to_user_offer_states(offer_like_model, user_offer_state_model)


def backwards(apps, schema_editor):
    offer_like_model = apps.get_model("offers", "OfferLike")
    user_offer_state_model = apps.get_model("offers", "UserOfferState")
    copy_user_offer_states_to_likes(user_offer_state_model, offer_like_model)


class Migration(migrations.Migration):
    dependencies = [
        ("offers", "0027_userofferstate"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
