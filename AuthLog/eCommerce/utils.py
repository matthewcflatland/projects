from django.core.mail import EmailMessage  # Used to create and send emails


def build_email(user, order, cart_items):
    subject = f"Order Confirmation {order.id}"  # Email subject line

    # Email message body, informing the user that their order has been placed successfully
    body = f"Hello {user.username},\n\nYour order #{order.id} has been placed successfully.\n\n"
    for item in cart_items:
        body += f"{item['product'].name} x {item['quantity']}\t${item['product'].price * item['quantity']}\n"
    body += f"\nSubtotal: ${order.total_price}\n\nThank you for shopping with us!"

    # Create the email object, setting the recipient to the user's email address
    email = EmailMessage(subject, body, to=[user.email])

    return email  # Return the email object so it can be sent later