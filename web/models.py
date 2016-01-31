from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Repository(models.Model):
    name = models.CharField(max_length=256)
    owner = models.CharField(max_length=256)
    # Settings
    contact_email = models.CharField(max_length=256, default=settings.AWS_SES_RETURN_PATH)

    def full_repository_name(self):
        return '{}/{}'.format(owner, name)

class Idea(models.Model):
    subscribers = models.ManyToManyField(User, related_name='ideas')
    repository = models.ForeignKey(Repository, related_name='ideas')
    number = models.PositiveIntegerField()
