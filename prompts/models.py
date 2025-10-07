from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models

class Prompt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    prompt = models.TextField()
    response = models.TextField(blank = True, null = True)
    created_at = models.DateTimeField(auto_now_add=True)