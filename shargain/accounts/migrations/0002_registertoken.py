# Generated by Django 4.1.4 on 2023-05-06 11:16

import functools
import secrets

from django.db import migrations, models

import shargain.accounts.models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="RegisterToken",
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
                (
                    "token",
                    models.CharField(
                        default=functools.partial(secrets.token_hex, *(16,), **{}),
                        max_length=32,
                        unique=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "valid_until",
                    models.DateTimeField(
                        default=shargain.accounts.models.get_default_valid_until
                    ),
                ),
                ("already_used", models.BooleanField(default=False)),
                ("description", models.CharField(blank=True, max_length=255)),
            ],
        ),
    ]