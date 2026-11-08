import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("offers", "0026_offer_passed_filters_and_index"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserOfferState",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("seen_at", models.DateTimeField(blank=True, null=True, verbose_name="Seen at")),
                ("liked_at", models.DateTimeField(blank=True, null=True, verbose_name="Liked at")),
                (
                    "offer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_states",
                        to="offers.offer",
                        verbose_name="Offer",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="offer_states",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
            options={
                "verbose_name": "User offer state",
                "verbose_name_plural": "User offer states",
            },
        ),
        migrations.AddConstraint(
            model_name="userofferstate",
            constraint=models.UniqueConstraint(
                fields=("user", "offer"),
                name="uniq_user_offer_state",
            ),
        ),
        migrations.AddConstraint(
            model_name="userofferstate",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("seen_at__isnull", False),
                    ("liked_at__isnull", False),
                    _connector="OR",
                ),
                name="user_offer_state_has_state",
            ),
        ),
    ]
