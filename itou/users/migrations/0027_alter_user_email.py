# Generated by Django 3.2.3 on 2021-07-05 13:37

import django.contrib.postgres.fields.citext
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0026_asp_previous_employer_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="email",
            field=django.contrib.postgres.fields.citext.CIEmailField(
                blank=True, db_index=True, max_length=254, null=True, unique=True, verbose_name="Adresse e-mail"
            ),
        ),
    ]
