# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from datetime import date
# Create your models here.

class Subscription(models.Model):
    name = models.CharField(max_length=255, default="")
    amount = models.DecimalField(max_digits=15, decimal_places=2, default="0.00")
    created_at = models.DateField(default=date.today)
    modified_at = models.DateField(default=date.today)

    def __str__(self):
        return self.name

class UserManager(BaseUserManager):
    def create_user(self, firstname, lastname, email, mobile, country, birthdate, gender, registered_by, device_token, social_id, profile_pic, is_agree, country_code, subscription=None, password=None):
        """
        Creates and saves a User with the given email, mobile, gender and password.
        """
        user = ""
        if not email:
            raise ValueError('Users must have an email address')

        if  registered_by != "manual":
            user = self.model(
                email=self.normalize_email(email),
                mobile=mobile,
                gender=gender,
                country=country,
                firstname=firstname,
                lastname=lastname,
                birthdate=birthdate,
                is_agree=is_agree,
                device_token=device_token,
                social_id=social_id,
                subscription=subscription,
                country_code=country_code,
                profile_pic=profile_pic,
                registered_by=registered_by
            )
        else:
            user = self.model(
                email=self.normalize_email(email),
                mobile=mobile,
                gender=gender,
                country=country,
                firstname=firstname,
                lastname=lastname,
                birthdate=birthdate,
                is_agree=is_agree,
                device_token=device_token,
                social_id=social_id,
                subscription=subscription,
                country_code=country_code,
                profile_pic=profile_pic,
                registered_by=registered_by,
                password=password
            )
        # user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, firstname, lastname, email, mobile, country, birthdate, gender, registered_by, device_token, social_id, profile_pic, is_agree, password, subscription=None, country_code="IN"):
        """
        Creates and saves a superuser with the given email, mobile, gender and password.
        """
        user = self.create_user(
            email=email,
            password=password,
            mobile=mobile,
            gender=gender,
            country=country,
            firstname=firstname,
            lastname=lastname,
            birthdate=birthdate,
            is_agree=is_agree,
            device_token=device_token,
            social_id=social_id,
            subscription=subscription,
            country_code=country_code,
            profile_pic=profile_pic,
            registered_by=registered_by
        )
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

def upload_to(instance, filename):
    return '/'.join([str(instance), filename])

class User(AbstractBaseUser, PermissionsMixin):
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255, default="", blank=True, null=True)
    email = models.EmailField(
        verbose_name='Email',
        max_length=255,
        unique=True,
    )
    mobile = models.CharField(max_length=255, default="", blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    birthdate = models.CharField(default='', blank=True, null=True, max_length=255)
    GENDER_CHOICES = (
        ('male', 'male'),
        ('female', 'female'),
    )
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    Register_Choices = (
        ('manual', 'manual'),
        ('facebook', 'facebook'),
        ('google', 'google'),
        ('apple', 'apple')
    )
    registered_by = models.CharField(max_length=10, choices=Register_Choices)
    device_token = models.CharField(max_length=5000, default='', blank=True, null=True)
    social_id = models.CharField(max_length=15000, default='', blank=True, null=True)
    subscription = models.ForeignKey(Subscription, blank=True, null=True, default="", related_name="subscribed", on_delete=models.DO_NOTHING)
    profile_pic = models.ImageField(upload_to=upload_to, blank=True, null=True)
    setup_count = models.CharField(default=0, max_length=255)
    is_setup = models.BooleanField(default=False)
    is_agree = models.BooleanField(default=0)
    is_registered = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_subscribed = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=True)
    country_code = models.CharField(max_length=5, default="", blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)
    modified_at = models.DateField(auto_now_add=True)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname', 'lastname', 'mobile', 'country', 'birthdate', 'gender', 'registered_by', 'device_token', 'social_id', 'profile_pic', 'is_agree']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.firstname, self.lastname)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.firstname

    @property
    def image_url(self):
        if self.profile_pic and hasattr(self.profile_pic, "url"):
            return self.profile_pic.url
        else:
            return None

class Income(models.Model):
    user = models.ForeignKey(User,related_name='income', on_delete=models.CASCADE)
    icon = models.CharField(max_length=1000)
    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default="0.00")
    currency = models.CharField(max_length=255, default="")
    created_at=models.DateField(auto_now_add=True)
    modified_at=models.DateField(auto_now=True)

    def __str__(self):
        return self.title

class Expense(models.Model):
    user = models.ForeignKey(User, related_name='expense',on_delete=models.CASCADE)
    icon = models.CharField(max_length=1000)
    title = models.CharField(max_length=255)
    spent_amount = models.DecimalField(max_digits=15, decimal_places=2, default="0.00")
    amount_limit = models.DecimalField(max_digits=15, decimal_places=2, default="0.00")
    time_range = models.CharField(max_length=255)
    currency = models.CharField(max_length=255, default="")
    created_at=models.DateField(auto_now_add=True)
    modified_at=models.DateField(auto_now=True)

    def __str__(self):
        return self.title      

class Goal(models.Model):
    user = models.ForeignKey(User,related_name='goal', on_delete=models.CASCADE)
    icon = models.CharField(max_length=1000)
    title = models.CharField(max_length=255)
    added_amount = models.DecimalField(max_digits=15, decimal_places=2, default="0.00")
    amount = models.DecimalField(max_digits=15, decimal_places=2, default="0.00")
    currency = models.CharField(max_length=255, default="")
    created_at=models.DateField(auto_now_add=True)
    modified_at=models.DateField(auto_now=True)
    is_completed =models.BooleanField(default=False)

    def __str__(self):
        return self.title        

class LogsAPI(models.Model):
    apiname = models.CharField(max_length=255)
    request_header = models.CharField(max_length=2000, default="")
    request_parameter = models.CharField(max_length=2000, default="")
    request_data = models.CharField(max_length=5000)
    response_data = models.CharField(max_length=5000)
    email = models.EmailField(verbose_name='Email', max_length=255, null=True, blank=True)
    status = models.BooleanField(default=False)
    created_date = models.DateField(auto_now_add=True)

class SourceIncome(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_main_income')
    title = models.CharField(max_length=255)
    icon = models.CharField(max_length=1000)
    spent_amount = models.DecimalField(max_digits=15, decimal_places=2, default="0.00")
    amount = models.DecimalField(max_digits=15, decimal_places=2, default="0.00")
    currency = models.CharField(max_length=255, default="")
    created_at = models.DateField(auto_now_add=True)
    modified_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title

class Exchangerate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="currency")
    currency_name = models.CharField(max_length=255)
    is_default=models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    modified_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.currency_name

class Location(models.Model):
    latitude = models.FloatField(blank=True, null=True, default="0.00")
    longitude = models.FloatField(blank=True, null=True, default="0.00")
    created_at = models.DateField(auto_now_add=True)
    modified_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.id

class Periodic(models.Model):
    start_date = models.DateField(blank=True ,null=True)
    end_date = models.DateField(blank=True ,null=True)
    week_days =models.CharField(max_length=5000, blank=True, null=True)
    prefix = models.CharField(max_length=255, blank=True, null=True)
    prefix_value = models.IntegerField(blank=True, null=True)
    status_days = models.CharField(max_length=5000, blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)
    modified_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

class Tag(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_tags") 
    name = models.CharField(max_length=255)
    created_at = models.DateField(default=date.today)
    modified_at = models.DateField(default=date.today)
    def __str__(self):
        return self.name  

class Debt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_debt") 
    icon = models.CharField(max_length=1000, default="")
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default="0.00")
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default="0.00")
    date = models.DateField()
    is_paid = models.BooleanField(default=False)
    is_partial_paid = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    currency = models.CharField(max_length=255, default="")
    created_at = models.DateField(auto_now_add=True)
    modified_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    title = models.CharField(max_length=255, default=None, blank=True, null=True)
    description = models.CharField(max_length=255, default=None, blank=True, null=True)
    transaction_amount = models.DecimalField(max_digits=15, decimal_places=2, default="0.00")
    converted_transaction = models.DecimalField(max_digits=15, decimal_places=2, default="0.00")
    converted_amount = models.DecimalField(max_digits=15, decimal_places=2, default="0.00")
    amount = models.DecimalField(max_digits=15, decimal_places=2, default="0.00")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    income_to = models.ForeignKey(Income, on_delete=models.CASCADE, blank=True, null=True, related_name="transaction_to_income")
    income_from = models.ForeignKey(Income, on_delete=models.CASCADE, blank=True, null=True, related_name="transaction_from_income")
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, blank=True, null=True, related_name="transaction_expense")
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, blank=True, null=True, related_name="transaction_goal")
    source = models.ForeignKey(SourceIncome, on_delete=models.CASCADE, blank=True, null=True, related_name="transaction_source")
    location=models.ForeignKey(Location, on_delete=models.CASCADE, blank=True, null=True, related_name="location")
    periodic=models.ForeignKey(Periodic, on_delete=models.CASCADE, blank=True, null=True, related_name="periodic")
    debt = models.ForeignKey(Debt, on_delete=models.CASCADE, blank=True, null=True, related_name="debt")
    tag = models.ManyToManyField(Tag, related_name="tags", blank=True)
    created_at=models.DateField()
    modified_at=models.DateField()
    is_completed = models.BooleanField(default=True)

    def __str__(self):
        return str(self.id)

class Setting(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name="user_settings") 
    notification = models.BooleanField(default=False)
    min_pass_3 = models.BooleanField(default=False)
    language = models.CharField(max_length=255, default=None, blank=True, null=True)
    currency = models.CharField(max_length=255, default=None, blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)
    modified_at = models.DateField(auto_now_add=True)

class notification(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    receiver_token = models.TextField(blank=True, null=True, default="")
    payload = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications", blank=True, null=True, default="")
    created_date = models.DateField(auto_now_add=True)
    modified_date = models.DateField(auto_now_add=True)