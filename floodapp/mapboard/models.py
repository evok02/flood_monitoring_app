from django.db import models


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
    x = models.DecimalField(max_digits=10, decimal_places=2)
    y = models.DecimalField(max_digits=10, decimal_places=2)
    dbmsnr = models.IntegerField()
    hzbnr01 = models.IntegerField(primary_key=True)
    typ = models.CharField(max_length=255)

    def __str__(self):
        return f"Station {self.hzbnr01}"
