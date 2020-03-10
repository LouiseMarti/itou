# Generated by Django 2.2.6 on 2019-11-04 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("job_applications", "0009_jobapplication_refusal_reason")]

    operations = [
        migrations.AlterField(
            model_name="jobapplication",
            name="refusal_reason",
            field=models.CharField(
                blank=True,
                choices=[
                    ("did_not_come", "Candidat non venu ou non joignable"),
                    ("unavailable", "Candidat indisponible ou non intéressé par le poste"),
                    ("non_eligible", "Candidat non éligible"),
                    (
                        "eligibility_doubt",
                        "Doute sur l'éligibilité du candidat (penser à renvoyer la personne vers un prescripteur)",
                    ),
                    ("incompatible", "Un des freins à l'emploi du candidat est incompatible avec le poste proposé"),
                    (
                        "prevent_objectives",
                        "L'embauche du candidat empêche la réalisation des objectifs du dialogue de gestion",
                    ),
                    ("no_position", "Pas de poste ouvert en ce moment"),
                    ("other", "Autre"),
                ],
                max_length=30,
                verbose_name="Motifs de refus",
            ),
        )
    ]
