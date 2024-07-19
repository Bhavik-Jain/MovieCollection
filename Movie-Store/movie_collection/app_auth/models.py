from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class RequestCount(models.Model):
    count = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.count)
