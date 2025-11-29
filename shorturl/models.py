from django.db import models
from django.db.models.signals import *
from django.conf import settings

class UserProfile(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    preferedurl=models.CharField(max_length=200)
    def __str__(self):  # __str__
        return (self.user.username)

class ShortURL(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    original_url = models.URLField(unique=True)
    short_code = models.CharField(max_length=10, unique=True)
    click_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    last_accessed_at = models.DateTimeField(null=True, blank=True)