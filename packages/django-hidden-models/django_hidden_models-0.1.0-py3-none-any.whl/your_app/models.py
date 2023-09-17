from django.db import models

from hidden_models.models import VisibleModel

# Create your models here.

class Book(VisibleModel):
    name = models.CharField(max_length=100)
