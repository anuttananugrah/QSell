from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from product.models import Product
from report.models import Report
from django.contrib import messages
from mail_manage.utils import send_report_notification

class ReportProductView(LoginRequiredMixin, View):

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        reason = request.POST.get("reason", "No reason provided")

        Report.objects.create(
            user=request.user,
            product=product,
            reason=reason
        )

        host_url = request.build_absolute_uri('/')[:-1]
        send_report_notification(product, request.user, reason, host_url)

        messages.warning(request, "Ad has been reported to administration for review.")
        return redirect('product_detail', pk=product_id)