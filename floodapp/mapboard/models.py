from django.db import models
from django.conf import settings

class Region(models.Model):
    name = models.CharField(max_length=100)  # Name of the region, e.g., "Vienna"
    latitude = models.FloatField()           # Latitude for the region center
    longitude = models.FloatField()          # Longitude for the region center

    def __str__(self):
        return self.name

class WaterLevel(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE)  # Link to Region
    water_level = models.FloatField()                             # Water level in meters
    risk_level = models.CharField(
        max_length=50,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')]
    )                                                             # Risk level: low, medium, high
    timestamp = models.DateTimeField(auto_now_add=True)           # When the data was recorded
    location_lat = models.FloatField(default=0.0)
    location_lon = models.FloatField(default=0.0)

class Station(models.Model):
    id = models.IntegerField(primary_key=True)
    hzbnr = models.IntegerField(null=True, blank=True, verbose_name="HZB Number")
    messstelle = models.CharField(max_length=255, null=True, blank=True, verbose_name="Measurement Point")
    dbmsnr = models.IntegerField(null=True, blank=True, verbose_name="DBMS Number")
    gewaesser = models.CharField(max_length=255, null=True, blank=True, verbose_name="Water Body")
    sachgebiet = models.CharField(max_length=255, null=True, blank=True, verbose_name="Field of Expertise")
    dienststelle = models.CharField(max_length=255, null=True, blank=True, verbose_name="Service Office")
    messstellenbetreiber = models.CharField(max_length=255, null=True, blank=True, verbose_name="Operator")
    orogr_einzugsgebiet = models.FloatField(null=True, blank=True, verbose_name="Catchment Area (km²)")
    exportzeitreihe = models.CharField(max_length=255, null=True, blank=True, verbose_name="Export Time Series")
    einheit = models.CharField(max_length=50, null=True, blank=True, verbose_name="Unit")
    exportzeitraum = models.CharField(max_length=255, null=True, blank=True, verbose_name="Export Period")
    prognose = models.BooleanField(default=False, verbose_name="Forecast")
    class Meta:
        db_table = "stations"
        verbose_name = "Station"
        verbose_name_plural = "Stations"

    def __str__(self):
        return self.messstelle or f"Station {self.hzbnr}"


class Measurement(models.Model):
    id = models.IntegerField(primary_key=True)
    # station_id = models.ForeignKey(Station, on_delete=models.CASCADE)
    station_id = models.IntegerField()
    timestamp = models.DateTimeField()
    wert = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    einheit = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'measurements'  # This links the model to the actual DB table
        verbose_name = 'Measurement'
        verbose_name_plural = 'Measurements'

    def __str__(self):
        return f"Measurement {self.id} - Station {self.station_id}"

class EmergencyReport(models.Model):
    # Link to a region
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    # Description of the emergency
    description = models.TextField()
    # Specific location
    location = models.CharField(max_length=255, blank=True, null=True)
    # Latitude and longitude for the emergency location
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    # Level of urgency
    urgency_level = models.CharField(
        max_length=50,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')]
    )
    # When the report was submitted
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report in {self.region.name} - {self.urgency_level}"


class Event(models.Model):
    title = models.CharField(max_length=200)
    start_time = models.DateTimeField(default = '2024-12-10 10:00:00+00')
    end_time = models.DateTimeField(default = '2024-12-10 10:00:00+00')
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

class DeleteEvent(models.Model):
    event_id = models.IntegerField()

    def __str__(self):
        return self.event_id
