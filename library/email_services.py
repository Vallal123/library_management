from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:

    """Service for sending formatted emails with error handling"""

    @staticmethod
    def send_welcome_email(user) -> bool:
        """
        Send welcome email to new user
        Returns: True if sent successfully, False otherwise
        """
        try:
            context = {
                'user_name': user.first_name or user.username,
                'explore_link': 'http://www.smartlibrary.com/books/',
            }

            html_message = render_to_string('emails/welcome_email.html', context)

            email_count = send_mail(
                subject='Welcome to Smart Library! 📚',
                message='Welcome to Smart Library',
                html_message=html_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )
            if email_count == 1:
                logger.info(f"Welcome email sent to {user.email}")
                return True
            else:
                logger.error(f"Failed to send welcome email to {user.email}")
                return False
        
        except Exception as e:
            logger.error(f"Exception sending email to {user.email}: {e}", exc_info=True)
            return False

    @staticmethod
    def send_borrow_confirmation(user, book) -> bool:
        """Send borrow confirmation email"""

        try:
            context = {
                'user_name': user.first_name or user.username,
                'book_title': book.title,
            }
        
            html_message = render_to_string('emails/borrow_confirmation.html', context)

            email_count = send_mail(
                subject=f'You borrowed "{book.title}"!',
                message=f'You borrowed {book.title}',
                html_message=html_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )

            if email_count == 1:
                logger.info(f"Borrow confirmation sent to {user.email} for {book.title}")
                return True
            else:
                logger.error(f"Failed to send borrow confimation to {user.email}")
                return False
        
        except Exception as e:
            logger.error(f"Exception sending borrow email: {e}", exc_info=True)
            return False

