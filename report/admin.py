from django.contrib import admin
from .models import Report

# Register your models here.

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'created_at')
    search_fields = ('product__title', 'user__username', 'reason')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
