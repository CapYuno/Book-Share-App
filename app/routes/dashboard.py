"""Dashboard blueprint."""
from flask import Blueprint, render_template
from app.models import Book, Borrower, Loan
from datetime import datetime

bp = Blueprint('dashboard', __name__, url_prefix='/')


@bp.route('/')
def index():
    """Dashboard home page."""
    # Get statistics
    total_books = Book.query.count()
    total_borrowers = Borrower.query.count()
    active_loans = Loan.query.filter_by(returned_at=None).count()
    overdue_loans = Loan.query.filter(
        Loan.returned_at.is_(None),
        Loan.due_at < datetime.utcnow()
    ).count()
    
    context = {
        'total_books': total_books,
        'total_borrowers': total_borrowers,
        'active_loans': active_loans,
        'overdue_loans': overdue_loans
    }
    
    return render_template('dashboard/index.html', **context)
