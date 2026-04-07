from django.urls import path
from report.views import ReportProductView

urlpatterns = [

    path('report/<int:product_id>/', ReportProductView.as_view(), name='report_product'),
]