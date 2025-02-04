# Generated by Django 3.1.7 on 2021-03-18 16:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("asp", "0003_auto_20210311_1147"),
        ("users", "0021_auto_20210318_1608"),
    ]

    operations = [
        migrations.AlterField(
            model_name="jobseekerprofile",
            name="hexa_commune",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="asp.commune",
                verbose_name="Commune (ref. ASP)",
            ),
        ),
        migrations.AlterField(
            model_name="jobseekerprofile",
            name="hexa_lane_number",
            field=models.CharField(blank=True, default="", max_length=10, verbose_name="Numéro de la voie"),
        ),
        migrations.AlterField(
            model_name="jobseekerprofile",
            name="hexa_non_std_extension",
            field=models.CharField(
                blank=True, default="", max_length=10, verbose_name="Extension de voie (non-repertoriée)"
            ),
        ),
        migrations.AlterField(
            model_name="jobseekerprofile",
            name="hexa_std_extension",
            field=models.CharField(
                blank=True,
                choices=[("B", "Bis"), ("T", "Ter"), ("Q", "Quater"), ("C", "Quinquies")],
                default="",
                max_length=1,
                verbose_name="Extension de voie",
            ),
        ),
    ]
