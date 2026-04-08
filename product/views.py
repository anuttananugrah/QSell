from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Case, When, Value, BooleanField
from django.views import View
from product.models import Product, ProductImage, Payment
from chat.models import Conversation, PhoneNumberRequest
from whishlist.models import Wishlist
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
import razorpay
from django.conf import settings
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from product.forms import ProductForm

class AddProductView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        profile = getattr(user, 'userprofile', None)
        is_complete = (user.first_name and user.last_name and profile and profile.phone_number and profile.location)
        if not is_complete:
            messages.warning(request, "Please complete your profile (full name, phone, and location) before adding products.")
            return redirect('edit_profile')
        
        form = ProductForm()
        return render(request, "add_product.html", {'form': form})

    def post(self, request):
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            
            images = request.FILES.getlist('images')
            for image in images:
                ProductImage.objects.create(product=product, image=image)
            return redirect("home")
        return render(request, "add_product.html", {'form': form})
    
class EditProductView(LoginRequiredMixin, View):
    def get(self, request, pk):
        product = get_object_or_404(Product, id=pk, seller=request.user)
        user = request.user
        profile = getattr(user, 'userprofile', None)
        is_complete = (user.first_name and user.last_name and profile and profile.phone_number and profile.location)
        if not is_complete:
            messages.warning(request, "Please complete your profile (full name, phone, and location) before managing products.")
            return redirect('edit_profile')
            
        form = ProductForm(instance=product)
        return render(request, "edit_product.html", {'form': form, 'product': product})

    def post(self, request, pk):
        product = get_object_or_404(Product, id=pk, seller=request.user)
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully.")
            return redirect("my_ads")
        return render(request, "edit_product.html", {'form': form, 'product': product})

class DeleteProductView(LoginRequiredMixin, View):
    def post(self, request, pk):
        product = get_object_or_404(Product, id=pk, seller=request.user)
        product.delete()
        messages.success(request, "Product deleted successfully.")
        return redirect("my_ads")

class MyAdsView(LoginRequiredMixin, View):
    def get(self, request):
        products = Product.objects.filter(seller=request.user)
        return render(request, "user_dash.html", {"products": products})
    

class BoostProductView(LoginRequiredMixin, View):
    def get(self, request, pk):
        product = get_object_or_404(Product, id=pk, seller=request.user)
        return render(request, "boost_product.html", {"product": product})

    def post(self, request, pk):
        product = get_object_or_404(Product, id=pk, seller=request.user)
        
        product.is_boosted = True
        product.boost_expiry = timezone.now() + timedelta(days=30)
        product.save()
        
        messages.success(request, f"Success! '{product.title}' has been boosted for 30 days.")
        return redirect('my_ads')

class ProductDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        product = get_object_or_404(Product, id=pk)
        
        product.views += 1
        product.save()

        context = {
            "product": product,
            "seller_ads_count": Product.objects.filter(seller=product.seller).count()
        }

        if request.user.is_authenticated:
            chat_req = Conversation.objects.filter(
                product=product,
                buyer=request.user
            ).first()
            context['user_chat_request'] = chat_req
            
            if chat_req and chat_req.status == 'rejected':
                last_update = chat_req.updated_at or chat_req.created_at
                next_request_time = last_update + timedelta(hours=24)
                context['can_re_request'] = timezone.now() > next_request_time
                if not context['can_re_request']:
                    diff = next_request_time - timezone.now()
                    context['wait_hours'] = diff.seconds // 3600
                    context['wait_minutes'] = (diff.seconds % 3600) // 60
            
            context['is_in_wishlist'] = Wishlist.objects.filter(
                user=request.user,
                product=product
            ).exists()
            
            context['phone_request'] = PhoneNumberRequest.objects.filter(
                buyer=request.user,
                product=product
            ).first()
        
        related_in_cat = list(Product.objects.filter(
            category=product.category,
            is_sold=False
        ).exclude(id=product.id).order_by('-created_at')[:4])
        
        if len(related_in_cat) < 4:
            recent_backup = Product.objects.filter(
                is_sold=False
            ).exclude(id=product.id).exclude(
                id__in=[p.id for p in related_in_cat]
            ).order_by('-created_at')[:4 - len(related_in_cat)]
            context['related_products'] = related_in_cat + list(recent_backup)
        else:
            context['related_products'] = related_in_cat

        return render(request, "product_detail.html", context)

class SearchView(View):
    def get(self, request):
        query = request.GET.get("q")
        category = request.GET.get("category")
        location = request.GET.get("location")

        products = Product.objects.filter(is_sold=False)
        if query:
            products = products.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query) |
                Q(category__name__icontains=query) |
                Q(search_tags__icontains=query)
            ).distinct()
        if category:
            products = products.filter(category_id=category)
        if location:
            products = products.filter(location__icontains=location)

        products = products.annotate(
            active_boost=Case(
                When(is_boosted=True, boost_expiry__gt=timezone.now(), then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        ).order_by('-active_boost', '-created_at')
        
        context = {
            'products': products,
            'category': {'name': f"Search Results for '{query}'" if query else "Search Results"}
        }
        return render(request, "product_listing.html", context)
    
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import traceback

@method_decorator(csrf_exempt, name='dispatch')
class CreateBoostOrderView(LoginRequiredMixin,View):
    def post(self, request, product_id):
        try:
            product = get_object_or_404(Product, id=product_id)

            client = razorpay.Client(
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
            )

            amount = 10000  # ₹99

            order = client.order.create({
                "amount": amount,
                "currency": "INR",
                "payment_capture": 1,
                "notes": {
                    "product_id": product.id,
                    "user_id": request.user.id
                }
            })

            Payment.objects.create(
                user=request.user,
                product=product,
                razorpay_order_id=order["id"],
                amount=amount,
                status="created"
            )

            return JsonResponse({
                "order_id": order["id"],
                "amount": amount,
                "key": settings.RAZORPAY_KEY_ID
            })

        except Exception as e:
            print("ERROR:", str(e))
            print(traceback.format_exc())
            return JsonResponse({"error": str(e)}, status=400)
        
@method_decorator(csrf_exempt, name='dispatch')
class VerifyPaymentView(View):

    def post(self, request):
        try:
            data = json.loads(request.body)

            client = razorpay.Client(
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
            )

            client.utility.verify_payment_signature({
                'razorpay_order_id': data['razorpay_order_id'],
                'razorpay_payment_id': data['razorpay_payment_id'],
                'razorpay_signature': data['razorpay_signature']
            })

            payment = Payment.objects.get(
                razorpay_order_id=data['razorpay_order_id']
            )

            payment.razorpay_payment_id = data['razorpay_payment_id']
            payment.razorpay_signature = data['razorpay_signature']
            payment.status = "success"
            payment.save()

            product = payment.product
            product.activate_boost()

            return JsonResponse({"status": "success"})

        except Exception as e:
            return JsonResponse({"status": "failed", "error": str(e)}, status=400)