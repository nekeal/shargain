# Generated by Django 3.1.7 on 2021-04-04 18:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("offers", "0004_auto_20210228_1359"),
    ]

    operations = [
        migrations.AddField(
            model_name="scrappingtarget",
            name="enable_notifications",
            field=models.BooleanField(
                default=True, verbose_name="Enable notifications"
            ),
        ),
    ]
