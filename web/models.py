from django.db import models
# Create your models here.

class Subscriber(models.Model):
    email = models.EmailField()
    valid = models.BooleanField(default=True)

class Repo(models.Model):
    name = models.CharField(max_length=256)
    owner = models.CharField(max_length=256)

    def full_repository_name(self):
        return '{}/{}'.format(owner, name)

class Idea(models.Model):
    subscribers = models.ManyToManyField(Subscriber, related_name='ideas')
    repository = models.ForeignKey(Repo, related_name='ideas')
    github_id = models.PositiveIntegerField()
