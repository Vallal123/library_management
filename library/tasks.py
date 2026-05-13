from celery import shared_task
from .email_services import EmailService
import logging
from django.conf import settings
from django.core.mail import send_mail
from datetime import timezone
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

@shared_task
def send_welcome_email_task(user_id):
    """Send welcom email asynchronously"""
    from .models import User
    user = User.objects.get(id=user_id)
    return EmailService.send_welcome_email(user)


@shared_task
def check_overdue_books():
    """Check and notify users about overdue books (runs daily)"""

    from .models import BorrowRecord

    try:
        overdue_records = BorrowRecord.objects.filter(
            is_returned=False,
            due_date__lt=timezone.now()
        )
        count = 0
        for record in overdue_records:
            send_overdue_notification_task.delay(record.id)
            count += 1

        logger.info(f"Checked {count} overdue books")
        return count
    except Exception as e:
        logger.error(f"Error in check_overdue_books: {e}", exc_info=True)
        return 0
    

@shared_task
def send_overdue_notification_task(borrow_record_id):
    """Send overdue notification email"""
    from .models import BorrowRecord

    try:
        record = BorrowRecord.objects.get(id=borrow_record_id)

        if record.is_returned:
            return False
        
        context = {
            'user_name': record.user.first_name or record.user.username,
            'book_title': record.book.title,
            'due_date': record.due_date,
            'days_overdue': (timezone.now() - record.due_date).days,
        }

        html_message = render_to_string('emails/overdue_notice.html', context)

        email_count = send_mail(
            subject=f'"{record.book.title}" is overdue!',
            message=f'{record.book.title} is overdue',
            html_message=html_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[record.user.email],
            fail_silently=False,
        )

        if email_count == 1:
            logger.info(f"Overdue notification sent to {record.user.email}")
            return True
        else:
            logger.error(f" Failed to send overdue notification")
            return False
    
    except Exception as e:
        logger.error(f"Error in send_overdue_notification_task: {e}", exc_info=True)
        return False