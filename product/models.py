from django.db import models
from account.models import User
from categories.models import Category
from django.utils import timezone
from datetime import timedelta
from cloudinary.models import CloudinaryField

# Create your models here.

class Product(models.Model):

    CONDITION_CHOICES = (
        ('Good', 'Good'),
        ('Standerd', 'Standerd'),
        ('Bad', 'Bad')
    )

    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.PositiveIntegerField()
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    location = models.CharField(max_length=200)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    views = models.PositiveIntegerField(default=0)
    is_sold = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    search_tags = models.TextField(blank=True, null=True, help_text="Search keywords separated by commas (e.g. iphone, apple, smartphone)")
    
    brand = models.CharField(max_length=100, blank=True, null=True)
    model_name = models.CharField(max_length=100, blank=True, null=True)
    year = models.PositiveIntegerField(blank=True, null=True)
    mileage = models.PositiveIntegerField(blank=True, null=True, help_text="In kilometres/miles, for vehicles only")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_boosted = models.BooleanField(default=False)
    boost_start = models.DateTimeField(null=True, blank=True)
    boost_expiry = models.DateTimeField(null=True, blank=True)
    def activate_boost(self):
        now = timezone.now()

        if self.boost_expiry and self.boost_expiry > now:
            self.boost_expiry += timedelta(days=30)
        else:
            self.is_boosted = True
            self.boost_start = now
            self.boost_expiry = now + timedelta(days=30)

        self.save()

    @property
    def is_boost_active(self):
        return self.is_boosted and self.boost_expiry and self.boost_expiry > timezone.now()
    def __str__(self):
        return self.title
        
class ProductImage(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = CloudinaryField('image')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.product.title

class Payment(models.Model):
    STATUS_CHOICES = (
        ('created', 'Created'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    razorpay_order_id = models.CharField(max_length=255)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)

    amount = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.title} - {self.status}"