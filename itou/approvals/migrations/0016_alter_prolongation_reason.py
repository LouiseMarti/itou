# Generated by Django 3.2.1 on 2021-07-21 07:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("approvals", "0015_alter_approval_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="prolongation",
            name="reason",
            field=models.CharField(
                choices=[
                    ("COMPLETE_TRAINING", "Fin d'une formation (6\u202fmois maximum)"),
                    ("RQTH", "RQTH (12\u202fmois maximum)"),
                    ("SENIOR", "50\u202fans et plus (12\u202fmois maximum)"),
                    (
                        "PARTICULAR_DIFFICULTIES",
                        "Difficultés particulières qui font obstacle à l'insertion durable dans "
                        "l’emploi (12\u202fmois maximum dans la limite de 5\u202fans)",
                    ),
                    ("HEALTH_CONTEXT", "Contexte sanitaire (12\u202fmois maximum)"),
                ],
                default="COMPLETE_TRAINING",
                max_length=30,
                verbose_name="Motif",
            ),
        ),
    ]
