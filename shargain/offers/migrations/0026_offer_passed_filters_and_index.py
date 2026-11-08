from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
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
    ]
