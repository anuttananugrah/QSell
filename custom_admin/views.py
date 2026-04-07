from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from account.models import User
from product.models import Product
from report.models import Report

class SuperuserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser
        
    def handle_no_permission(self):
        messages.error(self.request, "Access denied. Admin privileges required.")
        return redirect('home')

class DashboardView(SuperuserRequiredMixin, View):
    def get(self, request):
        users_count = User.objects.exclude(is_superuser=True).count()
        products_count = Product.objects.count()
        reports_count = Report.objects.filter(is_resolved=False).count()
        
        recent_reports = Report.objects.filter(is_resolved=False).order_by('-created_at')[:5]
        
        context = {
            'users_count': users_count,
            'products_count': products_count,
            'reports_count': reports_count,
            'recent_reports': recent_reports
        }
        return render(request, 'custom_admin/dashboard.html', context)

class AdminUsersList(SuperuserRequiredMixin, View):
    def get(self, request):
        users = User.objects.exclude(is_superuser=True).order_by('-date_joined')
        return render(request, 'custom_admin/users_list.html', {'users': users})

class AdminProductsList(SuperuserRequiredMixin, View):
    def get(self, request):
        products = Product.objects.all().order_by('-created_at')
        return render(request, 'custom_admin/products_list.html', {'products': products})

class AdminReportsList(SuperuserRequiredMixin, View):
    def get(self, request):
        reports = Report.objects.all().order_by('is_resolved', '-created_at')
        return render(request, 'custom_admin/reports_list.html', {'reports': reports})


def toggle_user_status(request, user_id):
    if not request.user.is_superuser:
        return redirect('home')
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    status = "activated" if user.is_active else "blocked"
    messages.success(request, f"User {user.first_name} has been {status}.")
    return redirect('custom_admin:users_list')

def delete_product(request, product_id):
    if not request.user.is_superuser:
        return redirect('home')
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, "Product deleted successfully.")
    return redirect('custom_admin:products_list')

def resolve_report(request, report_id):
    if not request.user.is_superuser:
        return redirect('home')
    report = get_object_or_404(Report, id=report_id)
    report.is_resolved = True
    report.save()
    messages.success(request, "Report marked as resolved.")
    return redirect('custom_admin:reports_list')
