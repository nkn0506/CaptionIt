from django.db import models

# Create your models here.
class UserDetails(models.Model):
    name=models.CharField(max_length=40)
    mobile=models.CharField(max_length=10)
    email=models.EmailField()
    password = models.CharField(max_length=32)
    description=models.TextField()


