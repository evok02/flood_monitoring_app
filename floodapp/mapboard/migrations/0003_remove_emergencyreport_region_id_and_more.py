# Generated by Django 4.2.16 on 2025-01-14 18:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mapboard', '0002_emergencyreport_region_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emergencyreport',
            name='region_id',
        ),
        migrations.AddField(
            model_name='emergencyreport',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mapboard.region'),
        ),
    ]
