# Generated by Django 5.0.3 on 2024-07-13 04:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("corecode", "0003_subject_contents"),
    ]

    operations = [
        migrations.CreateModel(
            name="Bill",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("prefix", models.CharField(max_length=45)),
                ("last_bill", models.IntegerField()),
            ],
        ),
    ]