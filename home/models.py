from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class Church(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    logo = models.ImageField(upload_to='church_logos/', null=True, blank=True)

    def __str__(self):
        return self.name


class Assembly(models.Model):
    name = models.CharField(max_length=255)
    church = models.ForeignKey(Church, related_name='assemblies', on_delete=models.CASCADE)
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class MemberManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Username field must be set')
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        return self.create_user(email, password, **extra_fields)


class Member(AbstractBaseUser, PermissionsMixin):
    #username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    phone_number = PhoneNumberField(null=True, blank=True)  # Use PhoneNumberField here
    address = models.CharField(max_length=255, null=True, blank=True)
    assembly = models.ForeignKey(Assembly, null=True, blank=True, related_name='members', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Admin rights
    date_joined = models.DateTimeField(default=timezone.now)
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('cashier', 'Cashier'),
        ('member', 'Member'),
    ]
    role = models.CharField(max_length=255, choices=ROLE_CHOICES, default='admin')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
        "phone_number",
        "address",
        #  "is_staff",
    ]  # Email and password are required by default

    objects = MemberManager()

    def __str__(self):
        return self.first_name + " " + self.last_name
