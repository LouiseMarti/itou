# Generated by Django 3.1.7 on 2021-03-24 16:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("employee_record", "0003_auto_20210318_1031"),
    ]

    operations = [
        migrations.AddField(
            model_name="employeerecord",
            name="asp_processing_label",
            field=models.CharField(blank=True, max_length=100, verbose_name="Libellé de traitement ASP"),
        ),
    ]
