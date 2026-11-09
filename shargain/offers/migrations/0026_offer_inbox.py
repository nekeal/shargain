import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def migrate_offer_likes(apps, schema_editor):
    OfferLike = apps.get_model("offers", "OfferLike")
    UserOfferState = apps.get_model("offers", "UserOfferState")
    batch = [
        UserOfferState(user_id=like.owner_id, offer_id=like.offer_id, liked_at=like.created_at)
        for like in OfferLike.objects.filter(owner__isnull=False).iterator(chunk_size=1000)
    ]
    if batch:
        UserOfferState.objects.bulk_create(batch, ignore_conflicts=True)


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("offers", "0025_merge_20261108"),
    ]

    operations = [
        migrations.AddField(
            model_name="offer",
            name="passed_filters",
            field=models.BooleanField(
                blank=True,
                default=None,
                help_text="Snapshot of whether the offer passed its scraping URL's notification filters at ingest.",
                null=True,
                verbose_name="Passed notification filters",
            ),
        ),
        migrations.AddIndex(
            model_name="offer",
            index=models.Index(
                fields=["target", "passed_filters", "created_at", "id"],
                name="offer_inbox_idx",
            ),
        ),
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
        migrations.RunPython(migrate_offer_likes, migrations.RunPython.noop),
        migrations.DeleteModel(name="OfferLike"),
    ]
