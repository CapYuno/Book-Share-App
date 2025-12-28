"""Reminder scheduler service using APScheduler."""
from flask import current_app
from app import db
from app.models import Loan, Notification
from app.services.email import EmailService
from datetime import datetime, timedelta


class ReminderScheduler:
    """Scheduler for processing and sending loan reminders."""
    
    @staticmethod
    def process_reminders():
        """Process all pending reminders.
        
        This should be called periodically (e.g., hourly or daily).
        """
        current_app.logger.info('Processing reminders...')
        
        # Get configuration
        days_before = current_app.config.get('REMINDER_BEFORE_DUE', 3)
        days_after = current_app.config.get('REMINDER_AFTER_DUE', 3)
        
        stats = {
            'before_due': 0,
            'on_due': 0,
            'after_due': 0,
            'failed': 0
        }
        
        # Find loans needing reminders
        active_loans = Loan.query.filter_by(returned_at=None).all()
        
        for loan in active_loans:
            notifications = ReminderScheduler._check_loan_notifications(
                loan, days_before, days_after
            )
            
            for notification_type in notifications:
                success = ReminderScheduler._send_reminder(loan, notification_type)
                if success:
                    stats[notification_type] += 1
                else:
                    stats['failed'] += 1
        
        current_app.logger.info(
            f"Reminders processed: {stats['before_due']} before-due, "
            f"{stats['on_due']} on-due, {stats['after_due']} overdue, "
            f"{stats['failed']} failed"
        )
        
        return stats
    
    @staticmethod
    def _check_loan_notifications(loan, days_before, days_after):
        """Check which notifications are needed for a loan.
        
        Args:
            loan: Loan instance
            days_before: Days before due to send reminder
            days_after: Days after due to send reminder
            
        Returns:
            List of notification types needed
        """
        needed = []
        now = datetime.utcnow()
        
        # Calculate reminder dates
        before_due_date = loan.due_at - timedelta(days=days_before)
        on_due_date = loan.due_at
        after_due_date = loan.due_at + timedelta(days=days_after)
        
        # Check if we need to send before-due reminder
        if (now.date() >= before_due_date.date() and 
            now.date() < on_due_date.date()):
            if not ReminderScheduler._notification_sent(loan, 'before_due'):
                needed.append('before_due')
        
        # Check if we need to send on-due reminder
        if now.date() == on_due_date.date():
            if not ReminderScheduler._notification_sent(loan, 'on_due'):
                needed.append('on_due')
        
        # Check if we need to send overdue reminder
        if now.date() >= after_due_date.date():
            if not ReminderScheduler._notification_sent(loan, 'after_due'):
                needed.append('after_due')
        
        return needed
    
    @staticmethod
    def _notification_sent(loan, kind):
        """Check if a notification has already been sent.
        
        Args:
            loan: Loan instance
            kind: Notification type
            
        Returns:
            True if already sent, False otherwise
        """
        existing = Notification.query.filter_by(
            loan_id=loan.id,
            kind=kind,
            status='sent'
        ).first()
        
        return existing is not None
    
    @staticmethod
    def _send_reminder(loan, notification_type):
        """Send a reminder and record the notification.
        
        Args:
            loan: Loan instance
            notification_type: Type of notification
            
        Returns:
            True if successful, False otherwise
        """
        # Send email
        success = EmailService.send_reminder(loan, notification_type)
        
        # Record notification
        notification = Notification(
            loan_id=loan.id,
            kind=notification_type,
            scheduled_at=datetime.utcnow(),
            sent_at=datetime.utcnow() if success else None,
            status='sent' if success else 'failed'
        )
        
        db.session.add(notification)
        db.session.commit()
        
        return success
    
    @staticmethod
    def schedule_notifications_for_loan(loan):
        """Pre-schedule notifications for a new loan.
        
        This creates pending notification records for a loan.
        
        Args:
            loan: Loan instance
        """
        days_before = current_app.config.get('REMINDER_BEFORE_DUE', 3)
        days_after = current_app.config.get('REMINDER_AFTER_DUE', 3)
        
        notifications = [
            {
                'kind': 'before_due',
                'scheduled_at': loan.due_at - timedelta(days=days_before)
            },
            {
                'kind': 'on_due',
                'scheduled_at': loan.due_at
            },
            {
                'kind': 'after_due',
                'scheduled_at': loan.due_at + timedelta(days=days_after)
            }
        ]
        
        for notif_data in notifications:
            notification = Notification(
                loan_id=loan.id,
                kind=notif_data['kind'],
                scheduled_at=notif_data['scheduled_at'],
                status='pending'
            )
            db.session.add(notification)
        
        db.session.commit()
        
        current_app.logger.info(
            f'Scheduled {len(notifications)} notifications for loan {loan.id}'
        )
