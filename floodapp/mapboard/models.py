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

    def __str__(self):
        return f"{self.region.name} - {self.water_level}m - {self.risk_level}"
