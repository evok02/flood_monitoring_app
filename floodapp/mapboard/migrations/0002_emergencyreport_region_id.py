# Generated by Django 4.2.16 on 2025-01-14 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapboard', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='emergencyreport',
            name='region_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
