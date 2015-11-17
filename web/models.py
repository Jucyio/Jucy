from django.db import models
# Create your models here.

class Subscriber(models.Model):
    email = models.EmailField()
    valid = models.BooleanField(default=True)

class Idea(models.Model):
    subscribers = models.ManyToManyField(Subscriber, related_name='ideas')
    github_id = models.PositiveIntegerField()
