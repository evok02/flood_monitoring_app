from django.db import models
from django import forms

class UserData(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=50)


    # def str(self):
    #     return f"{self.first_name} {self.last_name}"