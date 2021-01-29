# Generated by Django 3.1.5 on 2021-02-02 19:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("event_management", "0004_abstractparticipation_data"),
    ]

    operations = [
        migrations.CreateModel(
            name="EventTypePreference",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "section",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        default=None,
                        max_length=150,
                        null=True,
                        verbose_name="Section Name",
                    ),
                ),
                ("name", models.CharField(db_index=True, max_length=150, verbose_name="Name")),
                ("raw_value", models.TextField(blank=True, null=True, verbose_name="Raw Value")),
                (
                    "instance",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="event_management.eventtype"
                    ),
                ),
            ],
        ),
    ]