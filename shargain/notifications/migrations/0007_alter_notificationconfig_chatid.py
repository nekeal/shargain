from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("notifications", "0006_notificationconfig_owner"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notificationconfig",
            name="chatid",
            field=models.CharField(blank=True, db_index=True, max_length=100, verbose_name="Chat ID"),
        ),
    ]
