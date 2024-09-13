from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from month.models import MonthField
from phonenumber_field.modelfields import PhoneNumberField


class Church(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    logo = models.ImageField(upload_to='church_logos/', null=True, blank=True)
    active = models.BooleanField(default=True)
    monthlySubscriptionFee = models.DecimalField(default=0, decimal_places=2, max_digits=11,
                                                 verbose_name="Monthly Subscription Fee")
    date_joined = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name.upper()

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Churches'
        verbose_name = "Church"


class Assembly(models.Model):
    name = models.CharField(max_length=255)
    church = models.ForeignKey(Church, related_name='assemblies', on_delete=models.CASCADE)
    location = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.church.name.upper() + " / " + self.name.upper()

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Assemblies'
        verbose_name = 'Assembly'


class MemberManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Username field must be set')
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class Member(AbstractBaseUser, PermissionsMixin):
    #username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    phone_number = PhoneNumberField(null=True, blank=True)  # Use PhoneNumberField here
    address = models.TextField(max_length=255, null=True, blank=True)
    assembly = models.ForeignKey(Assembly, null=True, blank=True, related_name='members', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Admin rights
    date_joined = models.DateTimeField(default=timezone.now)
    date_of_birth = models.DateField(default=timezone.now)
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('cashier', 'Cashier'),
        ('member', 'Member'),
    ]
    profilePhoto = models.ImageField(upload_to='member-profiles/', null=True, blank=True)
    role = models.CharField(max_length=255, choices=ROLE_CHOICES, default='admin')
    SEX_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    ]
    sex = models.CharField(max_length=255, choices=SEX_CHOICES, default="Other")

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

    class Meta:
        ordering = ["last_name", "first_name"]
        verbose_name = "Member"
        verbose_name_plural = "Members"


class MonthlySubscription(models.Model):
    member = models.ForeignKey(Member, related_name='subscriptions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    subscription_month = MonthField()
    is_paid = models.BooleanField(default=False)
    owing_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Track owing amount

    def __str__(self):
        return f"{str(self.member)} - {self.subscription_month.strftime('%B %Y')}"

    def mark_as_paid(self, payment_amount):
        """
        Mark the subscription as paid or update the owing amount.
        """
        if payment_amount >= self.owing_amount:
            self.is_paid = True
            self.owing_amount = 0
        else:
            self.owing_amount -= payment_amount
        self.save()

    class Meta:
        unique_together=[("member", "subscription_month")]

CURRENCY_CHOICES = [
    ("$", "USD"),
    ("Z$", "ZWG")
]


class PaymentMethod(models.Model):
    church = models.ForeignKey(Church, related_name='payment_methods', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    currency = models.CharField(max_length=100, choices=CURRENCY_CHOICES, default='USD')
    incoming_payments = models.BooleanField(default=False, verbose_name="Incoming Payments")
    outgoing_payments = models.BooleanField(default=False, verbose_name="Outgoing Payments")
    available_balance = models.DecimalField(default=0, decimal_places=2, max_digits=11,
                                            verbose_name="Available_Balance")
    total_balance = models.DecimalField(default=0, decimal_places=2, max_digits=11, verbose_name="Total Balance")
    accountNumber = models.CharField(max_length=100, blank=True, null=True, verbose_name="Account Number")
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name.upper()

    class Meta:
        unique_together = [("church", "name")]
        verbose_name = "Payment Method"
        verbose_name_plural = "Payment Methods"


class Payment(models.Model):
    member = models.ForeignKey(Member, null=True, blank=True, related_name='payments', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    PAYMENT_TYPE_CHOICES = [
        ("Initial Balance", "Initial Balance"),
        ("Offering", "Offering"),
        ("Tithe", "Tithe"),
        ("Donation", "Donation"),
        ("Monthly Subscription", "Monthly Subscription"),
        ("Fundraising Contribution", "Fundraising Contribution"),
    ]
    type = models.CharField(max_length=255, choices=PAYMENT_TYPE_CHOICES)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{str(self.member)} - {self.amount} - {self.date}"

    def apply_to_subscriptions(self):
        """
        Apply payment to earliest outstanding subscriptions.
        """
        subscriptions = MonthlySubscription.objects.filter(member=self.member, is_paid=False).order_by(
            'subscription_month')
        remaining_amount = self.amount

        for subscription in subscriptions:
            if remaining_amount <= 0:
                break

            if remaining_amount >= subscription.owing_amount:
                # Pay off the whole owing amount for this month
                remaining_amount -= subscription.owing_amount
                subscription.mark_as_paid(subscription.owing_amount)
            else:
                # Partial payment, reduce the owing amount
                subscription.mark_as_paid(remaining_amount)
                remaining_amount = 0


class FundraisingProject(models.Model):
    church = models.ForeignKey(Church, related_name='fundraising_projects', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    currency = models.CharField(max_length=100, choices=CURRENCY_CHOICES, default='USD')
    target_amount = models.DecimalField(max_digits=15, decimal_places=2)
    raised_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["start_date", "end_date"]
        verbose_name = "Fundraising Project"
        verbose_name_plural = "Fundraising Projects"


class FundraisingContribution(models.Model):
    project = models.ForeignKey(FundraisingProject, related_name='contributions', on_delete=models.CASCADE)
    payment = models.OneToOneField(Payment, related_name='fundraising_contribution', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f"{self.payment.member} - {self.amount} - {self.project.title}"
