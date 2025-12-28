"""Admin blueprint for system management."""
from flask import Blueprint, render_template, redirect, url_for, flash, current_app, send_file, request
from app.models import Book, Borrower, Loan, db
from datetime import datetime
import csv
import io
from werkzeug.utils import secure_filename

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/')
def dashboard():
    """Admin dashboard."""
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
        'overdue_loans': overdue_loans,
        'reminder_before': current_app.config.get('REMINDER_BEFORE_DUE', 3),
        'reminder_after': current_app.config.get('REMINDER_AFTER_DUE', 3)
    }
    
    return render_template('admin/dashboard.html', **context)


@bp.route('/reminders/run', methods=['POST'])
def run_reminders():
    """Manually trigger reminder job."""
    from app.utils.scheduler_config import run_reminders_now
    
    try:
        stats = run_reminders_now()
        flash(
            f"Reminders sent! Before-due: {stats['before_due']}, "
            f"On-due: {stats['on_due']}, Overdue: {stats['after_due']}, "
            f"Failed: {stats['failed']}",
            'success'
        )
    except Exception as e:
        flash(f'Failed to send reminders: {str(e)}', 'error')
    
    return redirect(url_for('admin.dashboard'))


@bp.route('/export/<string:data_type>')
def export_data(data_type):
    """Export data to CSV."""
    if data_type not in ['books', 'borrowers', 'loans']:
        flash('Invalid export type', 'error')
        return redirect(url_for('admin.dashboard'))
    
    # Create CSV in memory
    output = io.StringIO()
    
    if data_type == 'books':
        books = Book.query.all()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Title', 'Author', 'ISBN', 'Genre', 'Year', 'Description', 'Available'])
        for book in books:
            writer.writerow([
                book.id, book.title, book.author, book.isbn or '',
                book.genre or '', book.year or '', book.description or '',
                'Yes' if book.is_available else 'No'
            ])
    
    elif data_type == 'borrowers':
        borrowers = Borrower.query.all()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Created At'])
        for borrower in borrowers:
            writer.writerow([
                borrower.id, borrower.name, borrower.email,
                borrower.phone or '', borrower.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
    
    elif data_type == 'loans':
        loans = Loan.query.all()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Book Title', 'Borrower Name', 'Borrowed At', 'Due At', 'Returned At', 'Status'])
        for loan in loans:
            status = 'Returned' if loan.returned_at else ('Overdue' if loan.due_at < datetime.utcnow() else 'Active')
            writer.writerow([
                loan.id, loan.book.title, loan.borrower.name,
                loan.borrowed_at.strftime('%Y-%m-%d %H:%M:%S'),
                loan.due_at.strftime('%Y-%m-%d %H:%M:%S'),
                loan.returned_at.strftime('%Y-%m-%d %H:%M:%S') if loan.returned_at else '',
                status
            ])
    
    # Prepare file for download
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'{data_type}_export_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'
    )


@bp.route('/import/books', methods=['POST'])
def import_books():
    """Import books from CSV file."""
    if 'file' not in request.files:
        flash('No file uploaded', 'error')
        return redirect(url_for('admin.dashboard'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('admin.dashboard'))
    
    if not file.filename.endswith('.csv'):
        flash('Please upload a CSV file', 'error')
        return redirect(url_for('admin.dashboard'))
    
    try:
        # Read CSV
        stream = io.StringIO(file.stream.read().decode('UTF8'), newline=None)
        reader = csv.DictReader(stream)
        
        imported = 0
        errors = []
        
        for row_num, row in enumerate(reader, start=2):  # Start at 2 because row 1 is header
            try:
                # Validate required fields
                if not row.get('Title') or not row.get('Author'):
                    errors.append(f"Row {row_num}: Title and Author are required")
                    continue
                
                # Create book
                book = Book(
                    title=row['Title'].strip(),
                    author=row['Author'].strip(),
                    isbn=row.get('ISBN', '').strip() or None,
                    genre=row.get('Genre', '').strip() or None,
                    year=int(row['Year']) if row.get('Year', '').strip() else None,
                    description=row.get('Description', '').strip() or None
                )
                db.session.add(book)
                imported += 1
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        db.session.commit()
        
        # Show results
        if imported > 0:
            flash(f'Successfully imported {imported} book(s)', 'success')
        if errors:
            flash(f'{len(errors)} error(s) occurred. Check console for details.', 'warning')
            for error in errors[:5]:  # Show first 5 errors
                flash(error, 'warning')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Import failed: {str(e)}', 'error')
    
    return redirect(url_for('admin.dashboard'))
