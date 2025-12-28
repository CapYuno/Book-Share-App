"""Email service for sending notifications."""
from flask import current_app, render_template_string
from flask_mail import Message
from app import mail
from app.models import Loan, Notification
from datetime import datetime


class EmailService:
    """Service for sending email notifications."""
    
    @staticmethod
    def send_email(to, subject, body_text, body_html=None):
        """Send an email.
        
        Args:
            to: Recipient email address (string or list)
            subject: Email subject
            body_text: Plain text body
            body_html: HTML body (optional)
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            msg = Message(
                subject=subject,
                recipients=[to] if isinstance(to, str) else to,
                body=body_text,
                html=body_html
            )
            
            mail.send(msg)
            current_app.logger.info(f'Email sent to {to}: {subject}')
            return True
            
        except Exception as e:
            current_app.logger.error(f'Failed to send email to {to}: {e}')
            return False
    
    @staticmethod
    def send_reminder(loan, reminder_type='on_due'):
        """Send a loan reminder email.
        
        Args:
            loan: Loan instance
            reminder_type: Type of reminder ('before_due', 'on_due', 'after_due')
            
        Returns:
            True if sent successfully, False otherwise
        """
        borrower = loan.borrower
        book = loan.book
        
        # Generate email content based on type
        if reminder_type == 'before_due':
            subject = f'Reminder: "{book.title}" due soon'
            days_until = (loan.due_at - datetime.utcnow()).days
            body = EmailService._generate_before_due_email(loan, days_until)
        elif reminder_type == 'on_due':
            subject = f'Reminder: "{book.title}" due today'
            body = EmailService._generate_on_due_email(loan)
        else:  # after_due
            subject = f'OVERDUE: "{book.title}" is overdue'
            days_overdue = (datetime.utcnow() - loan.due_at).days
            body = EmailService._generate_overdue_email(loan, days_overdue)
        
        # Send email
        success = EmailService.send_email(
            to=borrower.email,
            subject=subject,
            body_text=body
        )
        
        return success
    
    @staticmethod
    def _generate_before_due_email(loan, days_until):
        """Generate email body for before-due reminder."""
        template = """
Hello {{ borrower_name }},

This is a friendly reminder that your loan is due soon:

Book: {{ book_title }}
Author: {{ book_author }}
Due Date: {{ due_date }}
Days Remaining: {{ days_until }}

Please remember to return the book by the due date to avoid overdue status.

Thank you,
BookShare Library Management System
        """
        
        return render_template_string(
            template,
            borrower_name=loan.borrower.name,
            book_title=loan.book.title,
            book_author=loan.book.author,
            due_date=loan.due_at.strftime('%A, %B %d, %Y'),
            days_until=days_until
        ).strip()
    
    @staticmethod
    def _generate_on_due_email(loan):
        """Generate email body for on-due reminder."""
        template = """
Hello {{ borrower_name }},

This is a reminder that your loan is due TODAY:

Book: {{ book_title }}
Author: {{ book_author }}
Due Date: {{ due_date }}

Please return the book today to avoid overdue status.

Thank you,
BookShare Library Management System
        """
        
        return render_template_string(
            template,
            borrower_name=loan.borrower.name,
            book_title=loan.book.title,
            book_author=loan.book.author,
            due_date=loan.due_at.strftime('%A, %B %d, %Y')
        ).strip()
    
    @staticmethod
    def _generate_overdue_email(loan, days_overdue):
        """Generate email body for overdue reminder."""
        template = """
Hello {{ borrower_name }},

This is an OVERDUE notice for:

Book: {{ book_title }}
Author: {{ book_author }}
Due Date: {{ due_date }}
Days Overdue: {{ days_overdue }}

Please return this book as soon as possible.

Thank you,
BookShare Library Management System
        """
        
        return render_template_string(
            template,
            borrower_name=loan.borrower.name,
            book_title=loan.book.title,
            book_author=loan.book.author,
            due_date=loan.due_at.strftime('%A, %B %d, %Y'),
            days_overdue=days_overdue
        ).strip()
    
    @staticmethod
    def test_email_config():
        """Test email configuration by sending a test message.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            msg = Message(
                subject='BookShare Email Test',
                recipients=[current_app.config.get('MAIL_USERNAME', 'test@example.com')],
                body='This is a test email from BookShare Library Management System.'
            )
            mail.send(msg)
            return True
        except Exception as e:
            current_app.logger.error(f'Email test failed: {e}')
            return False
