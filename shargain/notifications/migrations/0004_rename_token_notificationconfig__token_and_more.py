# Generated by Django 4.1.4 on 2023-04-13 19:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("notifications", "0003_delete_notificationchannel"),
    ]

    operations = [
        migrations.RenameField(
            model_name="notificationconfig",
            old_name="token",
            new_name="_token",
        ),
        migrations.AlterField(
            model_name="notificationconfig",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]