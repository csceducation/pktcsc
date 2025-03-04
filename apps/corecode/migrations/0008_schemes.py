# Generated by Django 5.1 on 2024-12-11 09:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("corecode", "0007_accountheading"),
    ]

    operations = [
        migrations.CreateModel(
            name="Schemes",
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
                (
                    "scheme_status",
                    models.CharField(
                        blank=True,
                        choices=[("Active", "Active"), ("Inactive", "Inactive")],
                        max_length=200,
                    ),
                ),
                ("name", models.CharField(max_length=260, unique=True)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
            ],
            options={
                "ordering": ["name"],
            },
        ),
    ]
