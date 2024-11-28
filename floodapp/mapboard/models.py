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


class EmergencyReport(models.Model):
    # Link to a region
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    # Description of the emergency
    description = models.TextField()
    # Specific location
    location = models.CharField(max_length=255, blank=True, null=True)
    # Level of urgency
    urgency_level = models.CharField(
        max_length=50,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')]
    )
    # When the report was submitted
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report in {self.region.name} - {self.urgency_level}"