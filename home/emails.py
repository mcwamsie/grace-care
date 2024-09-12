from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.core.files.storage import default_storage
from home.models import Church  # Import the Company model


def send_welcome_email(user_email, first_name, password, church: Church):
    # Email subject and sender
    subject = f'Welcome to {church.name}'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [user_email]

    # Load HTML template and render it with context
    html_content = render_to_string('email_templates/onboarding.html', {
        'user_email': user_email,
        'user_name': first_name,
        'user': user_email,
        'church': church,
        'password': password
    })
    text_content = strip_tags(html_content)  # Fallback plain-text version

    # Create the email message
    email = EmailMultiAlternatives(subject, text_content, from_email, to_email)

    # Attach HTML content
    email.attach_alternative(html_content, "text/html")

    # Get the logo file from the company object
    if church.logo:
        logo_full_path = default_storage.path(church.logo.name)  # Full path to the logo

        # Attach the logo image with Content-ID (cid)
        with open(logo_full_path, 'rb') as logo_file:
            email.attach('logo.png', logo_file.read(), 'image/png')  # Attach the logo

    # Send the email
    email.send(fail_silently=False)

def send_email(email_address):
    pass

def send_html_email_with_logo(user_email, user_name, church:Church):
    subject = f'Welcome to {church.name}'
    from_email = 'noreply@example.com'  # Replace with your default sender email
    to_email = [user_email]

    # Load the HTML template and pass the context
    html_content = render_to_string('email_templates/test.html', {
        'user_name': user_name,
        'company_name': church.name,
    })
    text_content = strip_tags(html_content)

    # Create the email
    email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    email.attach_alternative(html_content, "text/html")

    # Attach the logo as an inline image
    if church.logo:
        logo_full_path = default_storage.path(church.logo.name)
        with open(logo_full_path, 'rb') as logo_file:
            email.attach('logo.png', logo_file.read(), 'image/png')

    # Send the email
    email.send(fail_silently=False)
