# Generated by Django 4.1.13 on 2024-11-18 02:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("assets", "0009_automationexecution_duration"),
    ]

    operations = [
        migrations.AlterField(
            model_name="automationexecution",
            name="duration",
            field=models.IntegerField(default=0, verbose_name="Duration"),
        ),
    ]
