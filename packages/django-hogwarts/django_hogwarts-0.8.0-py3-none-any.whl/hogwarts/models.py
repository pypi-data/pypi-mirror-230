from django.db import models

from django.contrib.auth import get_user_model


User = get_user_model()


# Create your models here.
class Example(models.Model):
    message = models.CharField(max_length=255)


class Article(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    beta = models.BooleanField(default=False)

