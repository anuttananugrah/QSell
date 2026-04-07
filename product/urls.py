from django.urls import path
from .views import *
from account.views import HomeView

urlpatterns = [

    path('product/<int:pk>/', ProductDetailView.as_view(), name="product_detail"),
    path('sell/', AddProductView.as_view(), name="add_product"),
    path('edit/<int:pk>/', EditProductView.as_view(), name="edit_product"),
    path('delete/<int:pk>/', DeleteProductView.as_view(), name="delete_product"),
    path('my-ads/', MyAdsView.as_view(), name="my_ads"),
    path('search/', SearchView.as_view(), name="search"),
    path('boost/<int:pk>/', BoostProductView.as_view(), name="boost_product"),
    path('boost/create/<int:product_id>/', CreateBoostOrderView.as_view(), name="create_boost"),
    path('boost/verify/', VerifyPaymentView.as_view(), name="verify_boost"),
]