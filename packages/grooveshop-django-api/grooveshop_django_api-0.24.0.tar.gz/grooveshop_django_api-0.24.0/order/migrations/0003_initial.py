# Generated by Django 4.2.4 on 2023-08-31 13:54
import django.db.models.deletion
from django.conf import settings
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("order", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="order_user",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
