from django.db import models

# Create your models here.
from django.db import models
import datetime
from django.utils import timezone
# Create your models here.

class Dashboard(models.Model):
    name = models.CharField(max_length=200)

    last_upgrade = models.CharField(max_length=200)
    vacunas_fabricadas = models.IntegerField(default=0)
    def __str__(self):
        return 'soy un dashboard'
