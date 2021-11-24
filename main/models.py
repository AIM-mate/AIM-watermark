from django.db import models

# Create your models here.

class Doc(models.Model):

    file = models.FileField(upload_to='documents/')

    def __str__(self):
        return str(self.pk)
