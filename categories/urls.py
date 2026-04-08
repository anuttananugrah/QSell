
from django.urls import path
from product.views import CategoryProductListView
from . import views


urlpatterns = [
    path('<slug:slug>/', CategoryProductListView.as_view(), name='category_products'),
    path('payment-success/', views.payment_success, name='payment_success'),

]