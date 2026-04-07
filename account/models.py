from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager
from random import randint

# Create your models here.

class CustomUserManger(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)
 
class User(AbstractUser):
    username=None
    email=models.EmailField(max_length=200, unique=True)
    is_verified=models.BooleanField(default=False)
    otp=models.CharField(max_length=10,null=True,blank=True)
    objects=CustomUserManger()
    def generate_otp(self):
        otp_number=str(randint(1000,9000))+str(self.id)
        self.otp=otp_number
        self.save()
    USERNAME_FIELD= "email"

    REQUIRED_FIELDS=[]

class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    profile_image = models.ImageField(upload_to="profile_images/", blank=True, null=True)

    phone_number = models.CharField(max_length=15)

    location = models.CharField(max_length=200)

    joined_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email

