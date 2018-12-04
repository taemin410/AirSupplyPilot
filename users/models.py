from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms.fields import ChoiceField
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import BaseUserManager
from authtools.models import AbstractEmailUser

class Clinic(models.Model):
    name = models.CharField(max_length=256)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    altitude = models.IntegerField()

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash((self.name, self.longitude, self.latitude))

    def __eq__(self, other):
        return (self.name, self.longitude, self.latitude) == (self.name, self.longitude, self.latitude)

class CustomUser(AbstractEmailUser):
    ROLES = (
        ('Clinic Manager', 'Clinic Manager'),
        ('Warehouse Personnel', 'Warehouse Personnel'),
        ('Dispatcher', 'Dispatcher'),
    )
    name = models.CharField(max_length=40, blank=True, default='')
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True, default='')
    last_name = models.CharField(max_length=30, blank=True, default='')
    role = models.CharField(choices=ROLES, max_length=30)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, null=True)

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
