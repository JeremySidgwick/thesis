from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    completed_tasks = models.IntegerField(default=0)

    # pour login avec email
    # email = models.EmailField(unique=True)
    # username = None
    # USERNAME_FIELD = 'email'

