# Generated by Django 3.1.8 on 2022-01-15 16:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("offers", "0009_offer_last_check_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="offer",
            name="main_image_url",
            field=models.URLField(blank=True, max_length=1024, verbose_name="Main image's URL"),
        ),
        migrations.AlterField(
            model_name="offer",
            name="url",
            field=models.URLField(max_length=1024),
        ),
        migrations.AlterField(
            model_name="scrappingtarget",
            name="url",
            field=models.URLField(max_length=1024),
        ),
    ]
