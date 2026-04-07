from django.shortcuts import render, get_object_or_404
from django.views import View
from product.models import Product
from categories.models import Category

class CategoryProductListView(View):
    def get(self, request, slug, *args, **kwargs):
        category = get_object_or_404(Category, slug=slug)
        products = Product.objects.filter(category=category)
        return render(request, 'product_listing.html', {
            'products': products,
            'category': category
        })