# Generated by Django 5.1 on 2024-09-08 01:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("students", "0006_student_m_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="student",
            name="password",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name="student",
            name="username",
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
