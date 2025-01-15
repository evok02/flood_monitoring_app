# Generated by Django 4.2.16 on 2025-01-09 15:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DeleteEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_id', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='EmergencyReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('urgency_level', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], max_length=50)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('start_time', models.DateTimeField(default='2024-12-10 10:00:00+00')),
                ('end_time', models.DateTimeField(default='2024-12-10 10:00:00+00')),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Station',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hzbnr', models.IntegerField(blank=True, null=True, verbose_name='HZB Number')),
                ('messstelle', models.CharField(blank=True, max_length=255, null=True, verbose_name='Measurement Point')),
                ('dbmsnr', models.IntegerField(blank=True, null=True, verbose_name='DBMS Number')),
                ('gewaesser', models.CharField(blank=True, max_length=255, null=True, verbose_name='Water Body')),
                ('sachgebiet', models.CharField(blank=True, max_length=255, null=True, verbose_name='Field of Expertise')),
                ('dienststelle', models.CharField(blank=True, max_length=255, null=True, verbose_name='Service Office')),
                ('messstellenbetreiber', models.CharField(blank=True, max_length=255, null=True, verbose_name='Operator')),
                ('orogr_einzugsgebiet', models.FloatField(blank=True, null=True, verbose_name='Catchment Area (km²)')),
                ('exportzeitreihe', models.CharField(blank=True, max_length=255, null=True, verbose_name='Export Time Series')),
                ('einheit', models.CharField(blank=True, max_length=50, null=True, verbose_name='Unit')),
                ('exportzeitraum', models.CharField(blank=True, max_length=255, null=True, verbose_name='Export Period')),
                ('prognose', models.BooleanField(default=False, verbose_name='Forecast')),
            ],
            options={
                'verbose_name': 'Station',
                'verbose_name_plural': 'Stations',
                'db_table': 'stations',
            },
        ),
        migrations.CreateModel(
            name='WaterLevel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('water_level', models.FloatField()),
                ('risk_level', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], max_length=50)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('location_lat', models.FloatField(default=0.0)),
                ('location_lon', models.FloatField(default=0.0)),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mapboard.region')),
            ],
        ),
        migrations.CreateModel(
            name='Measurement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('wert', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('einheit', models.CharField(blank=True, max_length=50, null=True)),
                ('station', models.ForeignKey(db_column='station_id', on_delete=django.db.models.deletion.CASCADE, related_name='measurements', to='mapboard.station')),
            ],
            options={
                'verbose_name': 'Measurement',
                'verbose_name_plural': 'Measurements',
                'db_table': 'measurements',
            },
        ),
    ]
