from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("offers", "0028_migrate_offerlike_to_userofferstate"),
    ]

    operations = [
        migrations.DeleteModel(
            name="OfferLike",
        ),
    ]
