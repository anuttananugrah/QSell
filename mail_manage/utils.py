from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from account.models import User

def send_account_otp(user_instance):
    """Generates and sends an OTP for account verification."""
    user_instance.generate_otp()
    otp = user_instance.otp
    
    subject = 'QSell - Verify Your Account'
    message = f'Welcome to QSell! Your verification code is: {otp}'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_instance.email]
    
    try:
        send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending OTP email: {e}")
        return False

def send_report_notification(product, reporter, reason, host_url=''):
    """Notifies the admin about a reported product."""
    subject = f"[URGENT] Ad Reported: {product.title}"
    
    product_url = f"{host_url}/product/{product.id}"
    
    message = f"""
    Dear Admin,

    A product has been reported by a user.

    Product: {product.title}
    URL: {product_url}
    Reporter: {reporter.first_name or 'A User'} ({reporter.email})
    Reason: {reason}

    Please review this as soon as possible.
    """
    
    from_email = 'noreply@qsell.com'
    recipient_list=[]
    filterd=User.objects.filter(is_superuser=True)
    for i in filterd:
        if i.is_superuser:
            recipient_list.append(i.email)
    try:
        send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=True,
        )
        return True
    except Exception as e:
        print(f"Error sending report notification: {e}")
        return False

def send_phone_request_notification(product, buyer):
    """Notifies the seller about a phone number request."""
    subject = f"Phone Number Request for {product.title}"
    
    seller_name = product.seller.first_name or "there"
    buyer_name = buyer.first_name or buyer.email

    message = (
        f"Hello {seller_name},\n\n"
        f"{buyer_name} is interested in your listing '{product.title}' "
        f"and has requested to see your phone number.\n\n"
        f"Please log in to QSell to approve or decline this request."
    )
    
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [product.seller.email]
    
    try:
        send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=True
        )
        return True
    except Exception as e:
        print(f"Error sending phone request notification: {e}")
        return False

def send_negotiation_request(product, buyer, amount, host_url=''):
    """Notifies the seller about a price negotiation request."""
    subject = f"Price Negotiation: {product.title}"
    
    seller_name = product.seller.first_name or "Seller"
    buyer_name = buyer.first_name or buyer.email
    product_url = f"{host_url}/product/{product.id}"

    message = (
        f"Hello {seller_name},\n\n"
        f"{buyer_name} has requested to negotiate the price for '{product.title}'.\n\n"
        f"Original Price: ₹{product.price}\n"
        f"Offered Price: ₹{amount}\n\n"
        f"Product URL: {product_url}\n\n"
        f"Please log in to QSell to approve or decline this offer in your message center."
    )
    
    recipient_list = [product.seller.email]
    
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
        return True
    except Exception as e:
        print(f"Error sending negotiation request email: {e}")
        return False

def send_negotiation_status(conversation, status, host_url=''):
    """Notifies the buyer about the status of their negotiation."""
    subject = f"Negotiation {status.title()}: {conversation.product.title}"
    
    buyer_name = conversation.buyer.first_name or "User"
    product_url = f"{host_url}/product/{conversation.product.id}"
    chat_url = f"{host_url}/chat/detail/{conversation.id}"

    if status == 'approved':
        message = (
            f"Hello {buyer_name},\n\n"
            f"Your negotiation request for '{conversation.product.title}' has been APPROVED.\n"
            f"Agreed Amount: ₹{conversation.negotiated_amount}\n\n"
            f"Chat session started. You can now chat with the seller here: {chat_url}\n\n"
            f"Thank you for using QSell."
        )
    else:
        message = (
            f"Hello {buyer_name},\n\n"
            f"Your negotiation request for '{conversation.product.title}' was declined by the seller.\n"
            f"You may try again after 24 hours or browse other listings: {product_url}"
        )
    
    recipient_list = [conversation.buyer.email]
    
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
        return True
    except Exception as e:
        print(f"Error sending negotiation status email: {e}")
        return False
