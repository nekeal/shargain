# Generated by Django 4.1.4 on 2025-07-13 18:35

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_registertoken"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="registertoken",
            options={
                "verbose_name": "Register token",
                "verbose_name_plural": "Register tokens",
            },
        ),
    ]
