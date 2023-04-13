# Generated by Django 3.1.8 on 2022-08-21 14:53

import django.db.models.deletion
from django.db import migrations, models


def migrate_scraping_urls_to_different_model(apps, schema_editor):
    ScrappingTarget = apps.get_model("offers", "ScrappingTarget")
    ScrappingUrl = apps.get_model("offers", "ScrapingUrl")
    targets = ScrappingTarget.objects.values("id", "url", "name")
    scraping_urls_to_create = [
        ScrappingUrl(name=target["name"], url=u, scraping_target_id=target["id"])
        for target in targets
        for u in target["url"]
    ]
    ScrappingUrl.objects.bulk_create(scraping_urls_to_create)


class Migration(migrations.Migration):
    dependencies = [
        ("offers", "0011_scrappingtarget_list_url"),
    ]

    operations = [
        migrations.CreateModel(
            name="ScrapingUrl",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Human readable name for the URL",
                        max_length=255,
                        verbose_name="Name",
                    ),
                ),
                (
                    "url",
                    models.URLField(
                        help_text="Target URL to one of the supported sites",
                        max_length=1024,
                        verbose_name="Target URL",
                    ),
                ),
                (
                    "scraping_target",
                    models.ForeignKey(
                        help_text="Group of scraping URLs",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="offers.scrappingtarget",
                        verbose_name="scraping target",
                    ),
                ),
            ],
            options={
                "verbose_name": "Scraping URL",
                "verbose_name_plural": "Scraping URLs",
            },
        ),
        migrations.RunPython(
            migrate_scraping_urls_to_different_model, migrations.RunPython.noop
        ),
    ]
