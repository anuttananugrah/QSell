from django.urls import path
from . import views

app_name = 'custom_admin'

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('users/', views.AdminUsersList.as_view(), name='users_list'),
    path('products/', views.AdminProductsList.as_view(), name='products_list'),
    path('reports/', views.AdminReportsList.as_view(), name='reports_list'),
    # Extra actions
    path('users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('products/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('reports/<int:report_id>/resolve/', views.resolve_report, name='resolve_report'),
]
