# Generated by Django 5.1 on 2024-12-07 11:26

import django.core.validators
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("students", "0007_alter_student_password_alter_student_username"),
    ]

    operations = [
        migrations.AddField(
            model_name="student",
            name="alt_number",
            field=models.CharField(
                blank=True,
                max_length=13,
                validators=[
                    django.core.validators.RegexValidator(
                        message="Entered mobile number isn't in a right format!",
                        regex="^[0-9]{10,15}$",
                    )
                ],
                verbose_name="Alternate Number",
            ),
        ),
        migrations.AlterField(
            model_name="exammodel",
            name="contected_mode",
            field=models.CharField(
                blank=True,
                choices=[("Online", "Online"), ("Offline", "Offline")],
                default=None,
                max_length=255,
                null=True,
                verbose_name="Mode",
            ),
        ),
        migrations.AlterField(
            model_name="exammodel",
            name="exam_date",
            field=models.DateField(
                default=django.utils.timezone.now, verbose_name="Exam date"
            ),
        ),
        migrations.AlterField(
            model_name="student",
            name="email",
            field=models.EmailField(
                blank=True, default="", max_length=254, null=True, verbose_name="Email"
            ),
        ),
    ]
