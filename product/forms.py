from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'category',
            'title',
            'description',
            'price',
            'condition',
            'location',
            'brand',
            'model_name',
            'year',
            'mileage',
            'search_tags',
            'latitude',
            'longitude'
        ]
