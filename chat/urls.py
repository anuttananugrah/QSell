from django.urls import path
from chat.views import *

urlpatterns = [

    path('conversations', ConversationListView.as_view(), name='conversations'),

    path('start/<int:product_id>/', StartConversationView.as_view(), name='start_chat'),
    path('<int:pk>/', ChatDetailView.as_view(), name='chat_detail'),
    path('negotiate/<int:product_id>/', NegotiatePriceView.as_view(), name='negotiate_price'),
    path('approve/<int:pk>/', ApproveChatView.as_view(), name='approve_chat'),
    path('reject/<int:pk>/', RejectChatView.as_view(), name='reject_chat'),

    # Phone Request
    path('request-phone/<int:product_id>/', RequestPhoneNumberView.as_view(), name='request_phone'),
    path('approve-phone/<int:pk>/', ApprovePhoneNumberRequestView.as_view(), name='approve_phone'),
    path('reject-phone/<int:pk>/', RejectPhoneNumberRequestView.as_view(), name='reject_phone'),
]