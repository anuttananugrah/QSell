from django.db import models
from account.models import User
from product.models import Product

# Create your models here.

class Conversation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="buyer")
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seller")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='approved')
    negotiated_amount = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Chat about {self.product.title} ({self.status})"
    
class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(null=True, blank=True)
    audio_file = models.FileField(upload_to='chat_audio/', null=True, blank=True)
    image = models.ImageField(upload_to='chat_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    def __str__(self):
        return self.message[:50] if self.message else "Voice Message"

class PhoneNumberRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="phone_buyer")
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="phone_seller")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Phone Request for {self.product.title} ({self.status})"