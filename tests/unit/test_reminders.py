"""Unit tests for email and reminder services."""
from app.models import Loan, Notification, Book, Borrower
from app.services.email import EmailService
from app.services.scheduler import ReminderScheduler
from datetime import datetime, timedelta


def test_email_template_generation(db, sample_book, sample_borrower):
    """Test that email templates are generated correctly."""
    # Create a loan
    loan = Loan(
        book_id=sample_book.id,
        borrower_id=sample_borrower.id,
        loaned_at=datetime.utcnow(),
        due_at=datetime.utcnow() + timedelta(days=14)
    )
    db.session.add(loan)
    db.session.commit()
    
    # Test before-due email
    body = EmailService._generate_before_due_email(loan, 3)
    assert 'due soon' in body.lower()
    assert sample_book.title in body
    assert sample_borrower.name in body
    assert '3' in body  # Days remaining
    
    # Test on-due email
    body = EmailService._generate_on_due_email(loan)
    assert 'due today' in body.lower()
    assert sample_book.title in body
    
    # Test overdue email
    body = EmailService._generate_overdue_email(loan, 2)
    assert 'overdue' in body.lower()
    assert sample_book.title in body
    assert '2' in body  # Days overdue


def test_notification_scheduling(db, sample_book, sample_borrower, app):
    """Test that notifications are scheduled correctly."""
    # Create a loan
    loan = Loan(
        book_id=sample_book.id,
        borrower_id=sample_borrower.id,
        loaned_at=datetime.utcnow(),
        due_at=datetime.utcnow() + timedelta(days=14)
    )
    db.session.add(loan)
    db.session.commit()
    
    # Schedule notifications
    with app.app_context():
        ReminderScheduler.schedule_notifications_for_loan(loan)
    
    # Check that notifications were created
    notifications = Notification.query.filter_by(loan_id=loan.id).all()
    
    # Should have 3 notifications (before_due, on_due, after_due)
    assert len(notifications) == 3
    
    # Verify types
    kinds = {n.kind for n in notifications}
    assert kinds == {'before_due', 'on_due', 'after_due'}
    
    # Verify all are pending
    for notification in notifications:
        assert notification.status == 'pending'
        assert notification.sent_at is None


def test_check_loan_notifications(db, sample_book, sample_borrower, app):
    """Test checking which notifications are needed."""
    with app.app_context():
        # Create a loan due in 3 days
        loan = Loan(
            book_id=sample_book.id,
            borrower_id=sample_borrower.id,
            loaned_at=datetime.utcnow(),
            due_at=datetime.utcnow() + timedelta(days=3)
        )
        db.session.add(loan)
        db.session.commit()
        
        # Check notifications needed (should trigger before_due)
        needed = ReminderScheduler._check_loan_notifications(loan, days_before=3, days_after=3)
        
        # Should need before_due reminder
        assert 'before_due' in needed


def test_notification_sent_check(db, sample_book, sample_borrower):
    """Test checking if notification was already sent."""
    # Create loan
    loan = Loan(
        book_id=sample_book.id,
        borrower_id=sample_borrower.id,
        loaned_at=datetime.utcnow(),
        due_at=datetime.utcnow() + timedelta(days=14)
    )
    db.session.add(loan)
    db.session.commit()
    
    # Check before sending
    assert ReminderScheduler._notification_sent(loan, 'before_due') is False
    
    # Create a sent notification
    notification = Notification(
        loan_id=loan.id,
        kind='before_due',
        scheduled_at=datetime.utcnow(),
        sent_at=datetime.utcnow(),
        status='sent'
    )
    db.session.add(notification)
    db.session.commit()
    
    # Check after sending
    assert ReminderScheduler._notification_sent(loan, 'before_due') is True
    
    # Other types should still be False
    assert ReminderScheduler._notification_sent(loan, 'on_due') is False


def test_overdue_detection(db, sample_book, sample_borrower):
    """Test that overdue loans are detected correctly."""
    # Create an overdue loan
    loan = Loan(
        book_id=sample_book.id,
        borrower_id=sample_borrower.id,
        loaned_at=datetime.utcnow() - timedelta(days=20),
        due_at=datetime.utcnow() - timedelta(days=5)
    )
    db.session.add(loan)
    db.session.commit()
    
    # Should be overdue
    assert loan.is_overdue is True
    
    # Return the book
    loan.returned_at = datetime.utcnow()
    db.session.commit()
    
    # Should no longer be overdue
    assert loan.is_overdue is False


def test_notification_model_relationships(db, sample_book, sample_borrower):
    """Test that notification-loan relationships work correctly."""
    # Create loan
    loan = Loan(
        book_id=sample_book.id,
        borrower_id=sample_borrower.id,
        loaned_at=datetime.utcnow(),
        due_at=datetime.utcnow() + timedelta(days=14)
    )
    db.session.add(loan)
    db.session.commit()
    
    # Create notification
    notification = Notification(
        loan_id=loan.id,
        kind='before_due',
        scheduled_at=datetime.utcnow(),
        status='pending'
    )
    db.session.add(notification)
    db.session.commit()
    
    # Test relationship
    assert notification.loan.id == loan.id
    assert notification in loan.notifications
    
    # Test to_dict
    notif_dict = notification.to_dict()
    assert notif_dict['loan_id'] == loan.id
    assert notif_dict['kind'] == 'before_due'
    assert notif_dict['status'] == 'pending'
