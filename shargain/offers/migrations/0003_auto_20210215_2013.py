# Generated by Django 3.1.6 on 2021-02-15 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("offers", "0002_scrappingtarget_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="offer",
            name="closed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="scrappingtarget",
            name="name",
            field=models.CharField(max_length=100),
        ),
    ]
