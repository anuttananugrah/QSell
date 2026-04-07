from django.urls import path
from whishlist.views import *

urlpatterns = [
    path('', WishlistListView.as_view(), name='wishlist'),
    path('add/<int:product_id>/', AddToWishlistView.as_view(), name='add_to_wishlist'),
    path('remove/<int:product_id>/', RemoveFromWishlistView.as_view(), name='remove_from_wishlist'),
]