
from django.urls import path
from .views import CategoryProductListView

urlpatterns = [
    path('category/<slug:slug>/', CategoryProductListView.as_view(), name='category_products'),
]