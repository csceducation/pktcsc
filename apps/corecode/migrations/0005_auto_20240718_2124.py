# Generated by Django 4.2.14 on 2024-07-18 15:54

from django.db import migrations
from ..models import Bill

def default_site_config(apps, schema_editor):
    Bill.objects.create(prefix="BN",last_bill=0)

class Migration(migrations.Migration):

    dependencies = [
        ("corecode", "0004_bill"),
    ]

    operations = [
        migrations.RunPython(default_site_config),
    ]