# Generated by Django 5.0.3 on 2024-07-11 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("students", "0004_alter_student_pincode"),
    ]

    operations = [
        migrations.AlterField(
            model_name="student",
            name="age",
            field=models.IntegerField(default=0, verbose_name="Age"),
        ),
    ]