# Generated by Django 3.0.4 on 2020-05-05 13:44

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("prescribers", "0015_auto_20200423_1700"),
    ]

    operations = [
        migrations.AddField(
            model_name="prescriberorganization",
            name="authorization_refused_at",
            field=models.DateTimeField(null=True, verbose_name="Date de refus de validation de l'habilitation"),
        ),
        migrations.AddField(
            model_name="prescriberorganization",
            name="authorization_refused_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="authorization_refused_set",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Validation de l'habilitation refusée par",
            ),
        ),
    ]
