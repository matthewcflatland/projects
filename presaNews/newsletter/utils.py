from django.core.mail import EmailMessage  # Used to create and send emails


def build_email(users, article):

    emails = []
    for user in users:
        # Email subject line
        subject = f"New article from subscriptions: {article.title}"

        # Email message body
        body = (f"Hello {user.username},\n\n"
                "There is a new article from your subscripiton:\n\n"
                f"127.0.0.1:8000/newsletter/article/{article.id}"
                )

        # Create the email object, setting the recipient to the user's email
        email = EmailMessage(subject, body, to=[user.email])
        emails.append(email)

    return emails  # Return the email object so it can be sent later
