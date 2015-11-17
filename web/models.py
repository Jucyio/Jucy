from django.db import models
# Create your models here.

class Subscriber(models.Model):
    email = models.EmailField()
    valid = models.BooleanField(default=True)
