import random
import string
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from .generators import random_password_generator
from .models import Member
from .emails import send_welcome_email  # Import your email-sending function
from .utils import calculateContributions


@receiver(post_save, sender=Member)
def send_welcome_email_to_user(sender, instance, created, **kwargs):
    if created:  # Send the email only when the profile is created
        #church = instance.assembly.church

        # Generate a random password
        #random_password = random_password_generator(8)

        # Set the password for the user
        #instance.set_password(random_password)
        #instance.save()
        if instance.assembly:
            calculateContributions(instance)
        # Send the welcome email with the random password
        #send_welcome_email(instance.email, instance.first_name, random_password, church)
