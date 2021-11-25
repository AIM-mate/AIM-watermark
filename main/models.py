from django.db import models
from django.utils import timezone

# Create your models here.

class Doc(models.Model):

    upload_date = models.DateTimeField(default=timezone.now)
    file = models.FileField(upload_to='documents/')

    def __str__(self):
        return str(self.pk)

