from django.db import models

# Create your models here.

class Doc(models.Model):

    time= models.DateTimeField(auto_now=True)
    file = models.FileField(upload_to='documents/')

    def __str__(self):
        return str(self.pk)
