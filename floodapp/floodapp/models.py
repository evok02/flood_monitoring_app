from django.db import models

class UserData(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    age = models.IntegerField()
    password = models.CharField(max_length=50)

    def str(self):
        return f"{self.first_name} {self.last_name}"