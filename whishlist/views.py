from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from product.models import Product
from .models import Wishlist
from django.contrib.auth.mixins import LoginRequiredMixin


class AddToWishlistView(LoginRequiredMixin, View):
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )
        return redirect('product_detail', pk=product_id)


class RemoveFromWishlistView(LoginRequiredMixin, View):
    def get(self, request, product_id):
        Wishlist.objects.filter(
            user=request.user,
            product_id=product_id
        ).delete()
        return redirect('product_detail', pk=product_id)


class WishlistListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        items = Wishlist.objects.filter(user=request.user)
        return render(request, "wishlist.html", {"items": items})