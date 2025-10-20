from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from .managers import UserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from datetime import timedelta
from django.utils import timezone

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        get_latest_by = 'updated_at'
        ordering = ('-updated_at', '-created_at',)
        abstract = True




class SubscriptionPlan(TimeStampedModel):
    DURATION_CHOICES = [
        ('free_trial', 'Free Trial'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    name = models.CharField(_("Name"), max_length=254, unique=True)
    duration = models.CharField(_("Subscription Duration"), max_length=10, choices=DURATION_CHOICES, default='free_trial')
    # price = models.DecimalField(_("Price"), max_digits=10, decimal_places=2)
    price = models.IntegerField(default=0) #cent
    features = models.TextField(_("Features"), null=True, blank=True)
    free_trial = models.BooleanField(default=True)
   

    def __str__(self):
        return self.name
    

    
    def get_display_price(self):
        print("{0:.2f}".format(self.price / 100), 'testtttt')
        return "{0:.2f}".format(self.price / 100)

class Subscription(TimeStampedModel):
    user = models.OneToOneField(
        'User',
        on_delete=models.CASCADE,
        related_name='subscription_name',
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.CASCADE,
    )
    start_date = models.DateTimeField(_("Start Date"), null=True, blank=True)
    end_date = models.DateTimeField(_("End Date"), null=True, blank=True)
    is_active = models.BooleanField(_("Is Active"), default=True)
    is_upgraded = models.BooleanField(default=False)
    payment_id = models.CharField(_("Payment ID"), max_length=100, null=True, blank=True)
    amount_paid = models.DecimalField(_("Amount Paid"), max_digits=10, decimal_places=2, null=True, blank=True)
    payment_status = models.CharField(_("Payment Status"), max_length=20, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Set a default start_date if it is not provided
        if self.start_date is None:
            self.start_date = timezone.now()
        super(Subscription, self).save(*args, **kwargs)

    def __str__(self):
        return f"Subscription for {self.user}"    



class User(AbstractBaseUser, PermissionsMixin):
    username = None
    email = models.EmailField(max_length=254, unique=True)
    name = models.CharField(max_length=254, null=True, blank=True)
    email_verification_code = models.CharField(max_length=50, null=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    subscription = models.OneToOneField(
        Subscription,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='user_subscription',
    )
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def get_absolute_url(self):
        return "/users/%i/" % (self.pk)
    
    def save(self, *args, **kwargs):
        # Hash the password if it's set and not hashed already
        if self.password and not self.password.startswith("pbkdf2_sha256$"):
            self.password = make_password(self.password)
        super(User, self).save(*args, **kwargs)





@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
        free_trial_plan_name = 'Free Trial'
        # Check if the Free Trial plan exists
        free_trial_plan, created = SubscriptionPlan.objects.get_or_create(
            name=free_trial_plan_name,
            defaults={
                'price': 0.00,  # Set the appropriate price for the Free Trial
                'features': 'Free Trial Features',
                'free_trial': True,
            }
        )

        # If the Free Trial plan didn't exist and was just created, set the start date to now
        if created:
            free_trial_plan.start_date = instance.date_joined
            free_trial_plan.save()

        subscription = Subscription.objects.create(
            user=instance,
            plan=free_trial_plan,
            start_date=instance.date_joined,
            # end_date=instance.date_joined + timedelta(days=30), 
            end_date = None
        )

        # Attach subscription to user model
        instance.subscription = subscription
        instance.save(update_fields=['subscription'])


