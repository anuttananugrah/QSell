from django.db import models
from account.models import User
from product.models import Product

# Create your models here.

class Report(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="submitted_reports")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reported_items")
    reason = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.product.title} reported by {self.user.username}"
