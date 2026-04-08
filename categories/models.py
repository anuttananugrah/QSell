from django.db import models
from django.utils.text import slugify

class Category(models.Model):

    CATEGORY_CHOICES = [
        ('mobiles', 'Mobiles'),
        ('laptops', 'Laptops'),
        ('fashion', 'Fashion'),
        ('camera', 'Camera'),
        ('home', 'Home'),
        ('cars', 'Cars'),
        ('gaming', 'Gaming'),
        ('audio', 'Audio'),
        ('bikes', 'Bikes'),
        ('watch', 'Watch'),
        ('books', 'Books'),
    ]

    name = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    slug = models.SlugField(unique=True, blank=True)
    icon = models.ImageField(upload_to="category_icons/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name