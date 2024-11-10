from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserAccount(models.Model):
    user = models.OneToOneField(User, related_name='account', on_delete=models.CASCADE)
    balance = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} | {self.balance}"