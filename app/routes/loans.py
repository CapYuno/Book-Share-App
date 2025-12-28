"""Loans blueprint."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Loan, Book, Borrower
from datetime import datetime, timedelta

bp = Blueprint('loans', __name__, url_prefix='/loans')


@bp.route('/')
def list_loans():
    """List all loans with optional filters."""
    filter_type = request.args.get('filter', 'active')
    
    if filter_type == 'overdue':
        loans = Loan.query.filter(
            Loan.returned_at.is_(None),
            Loan.due_at < datetime.utcnow()
        ).all()
    elif filter_type == 'returned':
        loans = Loan.query.filter(Loan.returned_at.isnot(None)).all()
    else:  # active
        loans = Loan.query.filter_by(returned_at=None).all()
    
    return render_template('loans/list.html', loans=loans, filter_type=filter_type)


@bp.route('/new', methods=['GET', 'POST'])
def create():
    """Create a new loan."""
    if request.method == 'POST':
        book_id = request.form.get('book_id', type=int)
        borrower_id = request.form.get('borrower_id', type=int)
        due_days = request.form.get('due_days', 14, type=int)
        
        # Explicit check: Prevent duplicate active loans for the same book
        existing_loan = Loan.query.filter_by(
            book_id=book_id,
            returned_at=None
        ).first()
        
        if existing_loan:
            flash('This book is already on loan and must be returned first!', 'error')
            return redirect(url_for('loans.create'))
        
        # Double-check book availability
        book = Book.query.get_or_404(book_id)
        if not book.is_available:
            flash('This book is not available for loan!', 'error')
            return redirect(url_for('loans.create'))
        
        # Create loan
        loan = Loan(
            book_id=book_id,
            borrower_id=borrower_id,
            due_at=datetime.utcnow() + timedelta(days=due_days)
        )
        db.session.add(loan)
        db.session.commit()
        
        # Schedule notifications
        from app.services.scheduler import ReminderScheduler
        ReminderScheduler.schedule_notifications_for_loan(loan)
        
        flash('Loan created successfully!', 'success')
        return redirect(url_for('books.detail', book_id=book_id))
    
    # GET request
    books = Book.query.all()
    borrowers = Borrower.query.all()
    return render_template('loans/form.html', books=books, borrowers=borrowers)


@bp.route('/<int:loan_id>/return', methods=['POST'])
def return_loan(loan_id):
    """Mark a loan as returned."""
    loan = Loan.query.get_or_404(loan_id)
    
    if loan.returned_at:
        flash('This loan has already been returned!', 'warning')
    else:
        loan.returned_at = datetime.utcnow()
        db.session.commit()
        flash('Loan returned successfully!', 'success')
    
    return redirect(url_for('loans.list_loans'))
