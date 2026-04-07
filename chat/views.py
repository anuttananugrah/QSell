from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.views import View
from chat.models import *
from product.models import Product
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from mail_manage.utils import send_phone_request_notification, send_negotiation_request, send_negotiation_status
from django.conf import settings
# Create your views here.

class StartConversationView(LoginRequiredMixin, View):

    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        seller = product.seller
        buyer = request.user
        
        if buyer == seller:
            messages.error(request, "You cannot chat with yourself.")
            return redirect('product_detail', pk=product_id)

        conversation, created = Conversation.objects.get_or_create(
            buyer=buyer,
            seller=seller,
            product=product
        )
        
        if created:
            messages.success(request, "Chat request sent to seller. Please wait for approval.")
            return redirect('product_detail', pk=product_id)
        
        if conversation.status == 'pending':
            messages.info(request, "Chat request is still pending approval.")
            return redirect('product_detail', pk=product_id)
        elif conversation.status == 'rejected':
            last_update = conversation.updated_at or conversation.created_at
            if timezone.now() > last_update + timedelta(hours=24):
                conversation.status = 'pending'
                conversation.save()
                messages.success(request, "Your previous request was declined, but 24 hours have passed. We've sent a new request to the seller.")
            else:
                wait_time = (last_update + timedelta(hours=24)) - timezone.now()
                hours, remainder = divmod(wait_time.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                messages.warning(request, f"Seller declined your request. Please wait {hours}h {minutes}m before re-requesting.")
            return redirect('product_detail', pk=product_id)
            
        return redirect('chat_detail', pk=conversation.id)

class ChatDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        conversation = get_object_or_404(Conversation, id=pk)
        
        if conversation.status != 'approved':
            messages.error(request, "This chat is not yet approved.")
            return redirect('conversations')

        Message.objects.filter(
            conversation=conversation, 
            is_read=False
        ).exclude(sender=request.user).update(is_read=True)
        
        messages_list = Message.objects.filter(conversation=conversation)
        return render(request, "chat_detail.html", {
            "conversation": conversation,
            "messages": messages_list
        })

    def post(self, request, pk):
        conversation = get_object_or_404(Conversation, id=pk)
        
        if conversation.status != 'approved':
            messages.error(request, "You cannot send messages in an unapproved chat.")
            return redirect('conversations')

        text = request.POST.get("message")
        audio = request.FILES.get("audio_file")
        image = request.FILES.get("image_file")
        
        if not text and not audio and not image:
            messages.error(request, "Cannot send an empty message.")
            return redirect('chat_detail', pk=pk)

        Message.objects.create(
            conversation=conversation,
            sender=request.user,
            message=text,
            audio_file=audio,
            image=image
        )

        return redirect('chat_detail', pk=pk)

class NegotiatePriceView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        amount = request.POST.get("amount")
        
        if not amount:
            messages.error(request, "Please enter a valid amount for negotiation.")
            return redirect('product_detail', pk=product_id)
            
        conversation, created = Conversation.objects.get_or_create(
            buyer=request.user,
            seller=product.seller,
            product=product
        )
        
        conversation.negotiated_amount = amount
        conversation.status = 'pending'
        conversation.save()
        
        host_url = request.build_absolute_uri('/')[:-1]
        if send_negotiation_request(product, request.user, amount, host_url):
            messages.success(request, f"Proposal of ₹{amount} sent to curator.")
        else:
            messages.warning(request, f"Proposal sent to curator, but notification failed.")
            
        return redirect('product_detail', pk=product_id)

class ConversationListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        
        active_conversations = Conversation.objects.filter(
            (Q(buyer=user) | Q(seller=user)),
            status='approved'
        ).order_by('-created_at')
        
        received_requests = Conversation.objects.filter(
            seller=user,
            status__in=['pending', 'rejected']
        ).order_by('-updated_at')
        
        sent_requests = Conversation.objects.filter(
            buyer=user,
            status__in=['pending', 'rejected']
        ).order_by('-updated_at')
        
        received_phone_requests = PhoneNumberRequest.objects.filter(
            seller=user
        ).order_by('-updated_at')
        
        sent_phone_requests = PhoneNumberRequest.objects.filter(
            buyer=user
        ).order_by('-updated_at')
        
        context = {
            'active_conversations': active_conversations,
            'received_requests': received_requests,
            'sent_requests': sent_requests,
            'received_phone_requests': received_phone_requests,
            'sent_phone_requests': sent_phone_requests,
            'conversations': active_conversations, # context_object_name fallback
        }
        
        return render(request, "conversations.html", context)

class ApproveChatView(LoginRequiredMixin, View):
    def get(self, request, pk):
        conversation = get_object_or_404(Conversation, id=pk, seller=request.user)
        old_status = conversation.status
        conversation.status = 'approved'
        conversation.save()
        
        if old_status == 'rejected':
            messages.success(request, f"Re-approved chat request from {conversation.buyer.username}.")
        else:
            messages.success(request, f"Chat request from {conversation.buyer.username} approved.")
            
        host_url = request.build_absolute_uri('/')[:-1]
        send_negotiation_status(conversation, 'approved', host_url)
        
        return redirect('conversations')

class RejectChatView(LoginRequiredMixin, View):
    def get(self, request, pk):
        conversation = get_object_or_404(Conversation, id=pk, seller=request.user)
        conversation.status = 'rejected'
        conversation.save()
        messages.warning(request, f"Chat request from {conversation.buyer.first_name} rejected.")
        
        host_url = request.build_absolute_uri('/')[:-1]
        send_negotiation_status(conversation, 'rejected', host_url)
        
        return redirect('conversations')

class RequestPhoneNumberView(LoginRequiredMixin, View):
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        if request.user == product.seller:
            messages.error(request, "This is your own ad.")
            return redirect('product_detail', pk=product_id)
            
        req, created = PhoneNumberRequest.objects.get_or_create(
            buyer=request.user,
            seller=product.seller,
            product=product
        )
        
        if created:
            if send_phone_request_notification(product, request.user):
                messages.success(request, "Request sent. Seller has been notified via email.")
            else:
                messages.success(request, "Request sent. But email notification failed.")
        else:
            messages.info(request, f"You already have a {req.status} request for this product.")
            
        return redirect('product_detail', pk=product_id)

class ApprovePhoneNumberRequestView(LoginRequiredMixin, View):
    def get(self, request, pk):
        req = get_object_or_404(PhoneNumberRequest, id=pk, seller=request.user)
        req.status = 'approved'
        req.save()
        messages.success(request, f"Phone request from {req.buyer.first_name} approved.")
        return redirect('conversations')

class RejectPhoneNumberRequestView(LoginRequiredMixin, View):
    def get(self, request, pk):
        req = get_object_or_404(PhoneNumberRequest, id=pk, seller=request.user)
        req.status = 'rejected'
        req.save()
        messages.warning(request, f"Phone request from {req.buyer.first_name} rejected.")
        return redirect('conversations')