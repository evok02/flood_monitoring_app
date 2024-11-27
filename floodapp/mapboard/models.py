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