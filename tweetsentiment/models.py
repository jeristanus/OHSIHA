from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

# UserSettings model contains all the settings of users
class UserSettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # The threshold for considering a tweet positive or negative
    polarity_interpretation_sensitivity = models.FloatField(default=0.2)
    # The last hashtag the user searched
    last_hashtag_searched = models.TextField(max_length=25, default="")


# Functions to automate the creation and updating of UserSettings, when User -model is referenced and changed
@receiver(post_save, sender=User)
def create_UserSettings(sender, instance, created, **kwargs):
    if created:
        UserSettings.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_UserSettings(sender, instance, **kwargs):
    instance.usersettings.save()
    pass
