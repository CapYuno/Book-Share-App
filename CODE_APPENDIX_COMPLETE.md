# Complete Code Appendix

## Configuration Files

### config.py

```python
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///bookshare.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    MAIL_SERVER = os.getenv('SMTP_HOST', 'localhost')
    MAIL_PORT = int(os.getenv('SMTP_PORT', 1025))
    MAIL_USE_TLS = os.getenv('SMTP_USE_TLS', 'False').lower() == 'true'
    MAIL_USE_SSL = os.getenv('SMTP_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = os.getenv('SMTP_USERNAME')
    MAIL_PASSWORD = os.getenv('SMTP_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('SMTP_FROM', 'BookShare <noreply@bookshare.local>')
    
    REMINDER_BEFORE_DUE = int(os.getenv('REMINDER_BEFORE_DUE', 3))
    REMINDER_AFTER_DUE = int(os.getenv('REMINDER_AFTER_DUE', 3))
    
    RECOMMENDATIONS_TOP_K = int(os.getenv('RECOMMENDATIONS_TOP_K', 3))
    TF_IDF_MIN_DF = int(os.getenv('TF_IDF_MIN_DF', 2))
    TF_IDF_MAX_FEATURES = int(os.getenv('TF_IDF_MAX_FEATURES', 1000))
    TF_IDF_NGRAM_RANGE = tuple(map(int, os.getenv('TF_IDF_NGRAM_RANGE', '1,2').split(',')))
    RECOMMENDATION_CACHE_PATH = os.getenv('RECOMMENDATION_CACHE_PATH', 'tfidf_cache.pkl')
    
    MAX_SEARCH_RESULTS = int(os.getenv('MAX_SEARCH_RESULTS', 100))


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
```

### run.py

```python
import os
from app import create_app

app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
```

## Application Core

### app/__init__.py

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from config import config

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    
    from app.routes import books, borrowers, loans, dashboard, recommendations, admin
    
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(books.bp)
    app.register_blueprint(borrowers.bp)
    app.register_blueprint(loans.bp)
    app.register_blueprint(recommendations.bp)
    app.register_blueprint(admin.bp)
    
    from app.utils import cli
    cli.register_commands(app)
    
    if not app.config.get('TESTING', False):
        from app.utils.scheduler_config import init_scheduler
        init_scheduler(app)
    
    with app.app_context():
        db.create_all()
    
    return app
```

### app/models.py

```python
from datetime import datetime
from app import db


class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    author = db.Column(db.String(200), nullable=False, index=True)
    isbn = db.Column(db.String(13), unique=True, index=True)
    year = db.Column(db.Integer)
    genre = db.Column(db.String(100), index=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    loans = db.relationship('Loan', backref='book', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Book {self.title} by {self.author}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'year': self.year,
            'genre': self.genre,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @property
    def is_available(self):
        active_loan = Loan.query.filter_by(
            book_id=self.id,
            returned_at=None
        ).first()
        return active_loan is None


class Borrower(db.Model):
    __tablename__ = 'borrowers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    email = db.Column(db.String(200), nullable=False, unique=True, index=True)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    loans = db.relationship('Loan', backref='borrower', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Borrower {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Loan(db.Model):
    __tablename__ = 'loans'
    
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False, index=True)
    borrower_id = db.Column(db.Integer, db.ForeignKey('borrowers.id'), nullable=False, index=True)
    loaned_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    due_at = db.Column(db.DateTime, nullable=False, index=True)
    returned_at = db.Column(db.DateTime)
    
    notifications = db.relationship('Notification', backref='loan', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Loan book_id={self.book_id} borrower_id={self.borrower_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'book_id': self.book_id,
            'borrower_id': self.borrower_id,
            'loaned_at': self.loaned_at.isoformat() if self.loaned_at else None,
            'due_at': self.due_at.isoformat() if self.due_at else None,
            'returned_at': self.returned_at.isoformat() if self.returned_at else None
        }
    
    @property
    def is_overdue(self):
        if self.returned_at:
            return False
        return datetime.utcnow() > self.due_at


class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('loans.id'), nullable=False, index=True)
    kind = db.Column(db.String(50), nullable=False)
    scheduled_at = db.Column(db.DateTime, nullable=False, index=True)
    sent_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')
    
    def __repr__(self):
        return f'<Notification loan_id={self.loan_id} kind={self.kind}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'loan_id': self.loan_id,
            'kind': self.kind,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'status': self.status
        }


class Setting(db.Model):
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Setting {self.key}={self.value}>'
    
    @staticmethod
    def get_value(key, default=None):
        setting = Setting.query.filter_by(key=key).first()
        return setting.value if setting else default
    
    @staticmethod
    def set_value(key, value):
        setting = Setting.query.filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            setting = Setting(key=key, value=value)
            db.session.add(setting)
        db.session.commit()
```

## Routes

### app/routes/dashboard.py

```python
from flask import Blueprint, render_template
from app.models import Book, Borrower, Loan
from datetime import datetime

bp = Blueprint('dashboard', __name__, url_prefix='/')


@bp.route('/')
def index():
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
```

### app/routes/books.py

```python
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from app import db
from app.models import Book
from sqlalchemy import or_

bp = Blueprint('books', __name__, url_prefix='/books')


@bp.route('/')
def list_books():
    query = request.args.get('q', '')
    
    if query:
        books = Book.query.filter(
            or_(
                Book.title.ilike(f'%{query}%'),
                Book.author.ilike(f'%{query}%'),
                Book.isbn.ilike(f'%{query}%'),
                Book.genre.ilike(f'%{query}%')
            )
        ).all()
    else:
        books = Book.query.all()
    
    return render_template('books/list.html', books=books, query=query)


@bp.route('/<int:book_id>')
def detail(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('books/detail.html', book=book)


@bp.route('/new', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        isbn = request.form.get('isbn', '').strip() or None
        genre = request.form.get('genre', '').strip() or None
        description = request.form.get('description', '').strip() or None
        
        if not title or not author:
            flash('Title and Author are required fields!', 'error')
            return render_template('books/form.html', book=None)
        
        if len(title) > 200:
            flash('Title must be 200 characters or less!', 'error')
            return render_template('books/form.html', book=None)
        
        if len(author) > 200:
            flash('Author must be 200 characters or less!', 'error')
            return render_template('books/form.html', book=None)
        
        if description and len(description) > 2000:
            flash('Description must be 2000 characters or less!', 'error')
            return render_template('books/form.html', book=None)
        
        book = Book(
            title=title,
            author=author,
            isbn=isbn,
            year=request.form.get('year', type=int),
            genre=genre,
            description=description
        )
        db.session.add(book)
        db.session.commit()
        
        try:
            from app.services.recommendations import rebuild_recommendation_cache
            rebuild_recommendation_cache()
            current_app.logger.info('Recommendation cache rebuilt after book creation')
        except Exception as e:
            current_app.logger.error(f'Failed to rebuild recommendation cache: {e}')
        
        flash('Book created successfully!', 'success')
        return redirect(url_for('books.detail', book_id=book.id))
    
    return render_template('books/form.html', book=None)



@bp.route('/<int:book_id>/edit', methods=['GET', 'POST'])
def edit(book_id):
    book = Book.query.get_or_404(book_id)
    
    if request.method == 'POST':
        book.title = request.form['title']
        book.author = request.form['author']
        book.isbn = request.form.get('isbn')
        book.year = request.form.get('year', type=int)
        book.genre = request.form.get('genre')
        book.description = request.form.get('description')
        db.session.commit()
        
        try:
            from app.services.recommendations import rebuild_recommendation_cache
            rebuild_recommendation_cache()
            current_app.logger.info('Recommendation cache rebuilt after book update')
        except Exception as e:
            current_app.logger.error(f'Failed to rebuild recommendation cache: {e}')
        
        flash('Book updated successfully!', 'success')
        return redirect(url_for('books.detail', book_id=book.id))
    
    return render_template('books/form.html', book=book)


@bp.route('/<int:book_id>/delete', methods=['POST'])
def delete(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    
    try:
        from app.services.recommendations import rebuild_recommendation_cache
        rebuild_recommendation_cache()
        current_app.logger.info('Recommendation cache rebuilt after book deletion')
    except Exception as e:
        current_app.logger.error(f'Failed to rebuild recommendation cache: {e}')
    
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('books.list_books'))


@bp.route('/api/search')
def api_search():
    query = request.args.get('q', '')
    
    books = Book.query.filter(
        or_(
            Book.title.ilike(f'%{query}%'),
            Book.author.ilike(f'%{query}%'),
            Book.isbn.ilike(f'%{query}%')
        )
    ).limit(10).all()
    
    return jsonify([book.to_dict() for book in books])


@bp.route('/api/autocomplete')
def api_autocomplete():
    from flask import session
    
    query = request.args.get('q', '').strip()
    
    search_history = session.get('book_search_history', [])
    
    results = []
    if query:
        books = Book.query.filter(
            or_(
                Book.title.ilike(f'%{query}%'),
                Book.author.ilike(f'%{query}%'),
                Book.genre.ilike(f'%{query}%')
            )
        ).limit(8).all()
        
        results = [{
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'genre': book.genre,
            'is_available': book.is_available
        } for book in books]
    
    return jsonify({
        'history': search_history[-5:],
        'results': results
    })


@bp.route('/api/history', methods=['POST'])
def api_save_history():
    from flask import session
    
    data = request.get_json()
    query = data.get('query', '').strip()
    
    if query:
        if 'book_search_history' not in session:
            session['book_search_history'] = []
        
        history = session['book_search_history']
        
        if query in history:
            history.remove(query)
        
        history.insert(0, query)
        
        session['book_search_history'] = history[:10]
        
        session.modified = True
    
    return jsonify({'success': True})


@bp.route('/api/history', methods=['DELETE'])
def api_clear_history():
    from flask import session
    
    session.pop('book_search_history', None)
    session.modified = True
    
    return jsonify({'success': True})
```

### app/routes/borrowers.py

```python
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app import db
from app.models import Borrower

bp = Blueprint('borrowers', __name__, url_prefix='/borrowers')


@bp.route('/')
def list_borrowers():
    borrowers = Borrower.query.all()
    return render_template('borrowers/list.html', borrowers=borrowers)


@bp.route('/<int:borrower_id>')
def detail(borrower_id):
    borrower = Borrower.query.get_or_404(borrower_id)
    return render_template('borrowers/detail.html', borrower=borrower)


@bp.route('/new', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        borrower = Borrower(
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form.get('phone')
        )
        db.session.add(borrower)
        db.session.commit()
        flash('Borrower created successfully!', 'success')
        return redirect(url_for('borrowers.detail', borrower_id=borrower.id))
    
    return render_template('borrowers/form.html', borrower=None)


@bp.route('/<int:borrower_id>/edit', methods=['GET', 'POST'])
def edit(borrower_id):
    borrower = Borrower.query.get_or_404(borrower_id)
    
    if request.method == 'POST':
        borrower.name = request.form['name']
        borrower.email = request.form['email']
        borrower.phone = request.form.get('phone')
        db.session.commit()
        flash('Borrower updated successfully!', 'success')
        return redirect(url_for('borrowers.detail', borrower_id=borrower.id))
    
    return render_template('borrowers/form.html', borrower=borrower)


@bp.route('/api/search')
def api_search():
    query = request.args.get('q', '')
    
    borrowers = Borrower.query.filter(
        Borrower.name.ilike(f'%{query}%') |
        Borrower.email.ilike(f'%{query}%')
    ).limit(10).all()
    
    return jsonify([borrower.to_dict() for borrower in borrowers])
```

### app/routes/loans.py

```python
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Loan, Book, Borrower
from datetime import datetime, timedelta

bp = Blueprint('loans', __name__, url_prefix='/loans')


@bp.route('/')
def list_loans():
    filter_type = request.args.get('filter', 'active')
    
    if filter_type == 'overdue':
        loans = Loan.query.filter(
            Loan.returned_at.is_(None),
            Loan.due_at < datetime.utcnow()
        ).all()
    elif filter_type == 'returned':
        loans = Loan.query.filter(Loan.returned_at.isnot(None)).all()
    else:
        loans = Loan.query.filter_by(returned_at=None).all()
    
    return render_template('loans/list.html', loans=loans, filter_type=filter_type)


@bp.route('/new', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        book_id = request.form.get('book_id', type=int)
        borrower_id = request.form.get('borrower_id', type=int)
        due_days = request.form.get('due_days', 14, type=int)
        
        existing_loan = Loan.query.filter_by(
            book_id=book_id,
            returned_at=None
        ).first()
        
        if existing_loan:
            flash('This book is already on loan and must be returned first!', 'error')
            return redirect(url_for('loans.create'))
        
        book = Book.query.get_or_404(book_id)
        if not book.is_available:
            flash('This book is not available for loan!', 'error')
            return redirect(url_for('loans.create'))
        
        loan = Loan(
            book_id=book_id,
            borrower_id=borrower_id,
            due_at=datetime.utcnow() + timedelta(days=due_days)
        )
        db.session.add(loan)
        db.session.commit()
        
        from app.services.scheduler import ReminderScheduler
        ReminderScheduler.schedule_notifications_for_loan(loan)
        
        flash('Loan created successfully!', 'success')
        return redirect(url_for('books.detail', book_id=book_id))
    
    books = Book.query.all()
    borrowers = Borrower.query.all()
    return render_template('loans/form.html', books=books, borrowers=borrowers)


@bp.route('/<int:loan_id>/return', methods=['POST'])
def return_loan(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    
    if loan.returned_at:
        flash('This loan has already been returned!', 'warning')
    else:
        loan.returned_at = datetime.utcnow()
        db.session.commit()
        flash('Loan returned successfully!', 'success')
    
    return redirect(url_for('loans.list_loans'))
```

### app/routes/recommendations.py

```python
from flask import Blueprint, jsonify, request, current_app
from app.models import Book, Borrower
from app.services.recommendations import get_recommendation_engine
import time

bp = Blueprint('recommendations', __name__, url_prefix='/recommendations')


@bp.route('/books/<int:book_id>')
def get_recommendations(book_id):
    start_time = time.time()
    
    book = Book.query.get_or_404(book_id)
    
    top_k = request.args.get('top', type=int) or \
            current_app.config.get('RECOMMENDATIONS_TOP_K', 3)
    
    engine = get_recommendation_engine()
    recommendations = engine.get_recommendations(book_id, top_k=top_k)
    
    recommended_books = []
    for rec_book_id, similarity_score in recommendations:
        rec_book = Book.query.get(rec_book_id)
        if rec_book:
            book_data = rec_book.to_dict()
            book_data['similarity_score'] = round(similarity_score, 4)
            recommended_books.append(book_data)
    
    latency_ms = (time.time() - start_time) * 1000
    
    return jsonify({
        'book_id': book_id,
        'book_title': book.title,
        'recommendations': recommended_books,
        'count': len(recommended_books),
        'latency_ms': round(latency_ms, 2),
        'algorithm': 'TF-IDF + Cosine Similarity'
    })


@bp.route('/borrowers/<int:borrower_id>')
def get_borrower_recommendations(borrower_id):
    start_time = time.time()
    
    borrower = Borrower.query.get_or_404(borrower_id)
    
    top_k = request.args.get('top', type=int) or \
            current_app.config.get('RECOMMENDATIONS_TOP_K', 3)
    
    engine = get_recommendation_engine()
    recommendations = engine.get_recommendations_for_borrower(borrower_id, top_k=top_k)
    
    recommended_books = []
    for rec_book_id, similarity_score, source in recommendations:
        rec_book = Book.query.get(rec_book_id)
        if rec_book:
            book_data = rec_book.to_dict()
            book_data['similarity_score'] = round(similarity_score, 4)
            recommended_books.append(book_data)
    
    latency_ms = (time.time() - start_time) * 1000
    
    return jsonify({
        'borrower_id': borrower_id,
        'borrower_name': borrower.name,
        'recommendations': recommended_books,
        'count': len(recommended_books),
        'latency_ms': round(latency_ms, 2),
        'algorithm': 'TF-IDF + Cosine Similarity (History-Based)'
    })


@bp.route('/rebuild', methods=['POST'])
def rebuild_cache():
    from app.services.recommendations import rebuild_recommendation_cache
    
    start_time = time.time()
    engine = rebuild_recommendation_cache()
    latency_ms = (time.time() - start_time) * 1000
    
    return jsonify({
        'status': 'success',
        'message': 'Recommendation cache rebuilt',
        'num_books': len(engine.book_ids),
        'num_features': engine.tfidf_matrix.shape[1] if engine.tfidf_matrix is not None else 0,
        'rebuild_time_ms': round(latency_ms, 2)
    })
```

### app/routes/admin.py

```python
from flask import Blueprint, render_template, redirect, url_for, flash, current_app, send_file, request
from app.models import Book, Borrower, Loan, db
from datetime import datetime
import csv
import io
from werkzeug.utils import secure_filename

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/')
def dashboard():
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
    if data_type not in ['books', 'borrowers', 'loans']:
        flash('Invalid export type', 'error')
        return redirect(url_for('admin.dashboard'))
    
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
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'{data_type}_export_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'
    )


@bp.route('/import/books', methods=['POST'])
def import_books():
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
        stream = io.StringIO(file.stream.read().decode('UTF8'), newline=None)
        reader = csv.DictReader(stream)
        
        imported = 0
        errors = []
        
        for row_num, row in enumerate(reader, start=2):
            try:
                if not row.get('Title') or not row.get('Author'):
                    errors.append(f"Row {row_num}: Title and Author are required")
                    continue
                
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
        
        if imported > 0:
            flash(f'Successfully imported {imported} book(s)', 'success')
        if errors:
            flash(f'{len(errors)} error(s) occurred. Check console for details.', 'warning')
            for error in errors[:5]:
                flash(error, 'warning')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Import failed: {str(e)}', 'error')
    
    return redirect(url_for('admin.dashboard'))
```

## Services

### app/services/recommendations.py

```python
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.models import Book
from flask import current_app
import pickle
import os


class RecommendationEngine:
    
    def __init__(self):
        self.vectorizer = None
        self.tfidf_matrix = None
        self.book_ids = []
        self.is_fitted = False
        
    def _prepare_features(self, book):
        features = []
        
        if book.title:
            features.append(book.title.lower())
            features.append(book.title.lower())
        
        if book.author:
            features.append(book.author.lower())
            features.append(book.author.lower())
        
        if book.genre:
            features.append(book.genre.lower())
            features.append(book.genre.lower())
            features.append(book.genre.lower())
        
        if book.description:
            features.append(book.description.lower())
        
        return ' '.join(features)
    
    def build_model(self, books=None):
        if books is None:
            books = Book.query.all()
        
        if not books:
            current_app.logger.warning('No books available to build recommendation model')
            return
        
        feature_texts = []
        self.book_ids = []
        
        for book in books:
            feature_texts.append(self._prepare_features(book))
            self.book_ids.append(book.id)
        
        min_df = current_app.config.get('TF_IDF_MIN_DF', 2)
        max_features = current_app.config.get('TF_IDF_MAX_FEATURES', 1000)
        ngram_range = current_app.config.get('TF_IDF_NGRAM_RANGE', (1, 2))
        
        self.vectorizer = TfidfVectorizer(
            min_df=min_df,
            max_features=max_features,
            ngram_range=ngram_range,
            stop_words='english',
            strip_accents='unicode',
            lowercase=True
        )
        
        self.tfidf_matrix = self.vectorizer.fit_transform(feature_texts)
        self.is_fitted = True
        
        current_app.logger.info(
            f'Built TF-IDF model: {len(books)} books, '
            f'{self.tfidf_matrix.shape[1]} features'
        )
    
    def get_recommendations(self, book_id, top_k=3):
        if not self.is_fitted:
            current_app.logger.warning('Model not fitted, building now...')
            self.build_model()
        
        try:
            book_idx = self.book_ids.index(book_id)
        except ValueError:
            current_app.logger.error(f'Book {book_id} not found in model')
            return []
        
        book_vector = self.tfidf_matrix[book_idx]
        similarities = cosine_similarity(book_vector, self.tfidf_matrix).flatten()
        
        similar_indices = similarities.argsort()[::-1]
        
        recommendations = []
        for idx in similar_indices:
            if self.book_ids[idx] != book_id:
                recommendations.append((
                    self.book_ids[idx],
                    float(similarities[idx])
                ))
                if len(recommendations) >= top_k:
                    break
        
        return recommendations
    
    def get_recommendations_for_borrower(self, borrower_id, top_k=3):
        from app.models import Loan
        
        past_loans = Loan.query.filter_by(
            borrower_id=borrower_id
        ).filter(
            Loan.returned_at.isnot(None)
        ).order_by(Loan.returned_at.desc()).limit(5).all()
        
        if not past_loans:
            return []
        
        all_recommendations = {}
        
        for loan in past_loans:
            book_recs = self.get_recommendations(loan.book_id, top_k=10)
            for book_id, score in book_recs:
                if book_id in all_recommendations:
                    all_recommendations[book_id] = (
                        all_recommendations[book_id] + score
                    ) / 2
                else:
                    all_recommendations[book_id] = score
        
        sorted_recs = sorted(
            all_recommendations.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]
        
        return [(book_id, score, None) for book_id, score in sorted_recs]
    
    def save_cache(self, cache_path='tfidf_cache.pkl'):
        if not self.is_fitted:
            current_app.logger.warning('Cannot save unfitted model')
            return
        
        cache_data = {
            'vectorizer': self.vectorizer,
            'tfidf_matrix': self.tfidf_matrix,
            'book_ids': self.book_ids
        }
        
        with open(cache_path, 'wb') as f:
            pickle.dump(cache_data, f)
        
        current_app.logger.info(f'Saved recommendation cache to {cache_path}')
    
    def load_cache(self, cache_path='tfidf_cache.pkl'):
        if not os.path.exists(cache_path):
            return False
        
        try:
            with open(cache_path, 'rb') as f:
                cache_data = pickle.load(f)
            
            self.vectorizer = cache_data['vectorizer']
            self.tfidf_matrix = cache_data['tfidf_matrix']
            self.book_ids = cache_data['book_ids']
            self.is_fitted = True
            
            current_app.logger.info(
                f'Loaded recommendation cache from {cache_path}'
            )
            return True
        except Exception as e:
            current_app.logger.error(f'Failed to load cache: {e}')
            return False


_recommendation_engine = None


def get_recommendation_engine():
    global _recommendation_engine
    
    if _recommendation_engine is None:
        _recommendation_engine = RecommendationEngine()
        
        cache_path = current_app.config.get(
            'RECOMMENDATION_CACHE_PATH',
            'tfidf_cache.pkl'
        )
        
        if not _recommendation_engine.load_cache(cache_path):
            current_app.logger.info('Building new recommendation model...')
            _recommendation_engine.build_model()
    
    return _recommendation_engine


def rebuild_recommendation_cache():
    global _recommendation_engine
    
    engine = RecommendationEngine()
    engine.build_model()
    
    cache_path = current_app.config.get(
        'RECOMMENDATION_CACHE_PATH',
        'tfidf_cache.pkl'
    )
    engine.save_cache(cache_path)
    
    _recommendation_engine = engine
    
    return engine
```

### app/services/email.py

```python
from flask import current_app, render_template_string
from flask_mail import Message
from app import mail
from app.models import Loan, Notification
from datetime import datetime


class EmailService:
    
    @staticmethod
    def send_email(to, subject, body_text, body_html=None):
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
        borrower = loan.borrower
        book = loan.book
        
        if reminder_type == 'before_due':
            subject = f'Reminder: "{book.title}" due soon'
            days_until = (loan.due_at - datetime.utcnow()).days
            body = EmailService._generate_before_due_email(loan, days_until)
        elif reminder_type == 'on_due':
            subject = f'Reminder: "{book.title}" due today'
            body = EmailService._generate_on_due_email(loan)
        else:
            subject = f'OVERDUE: "{book.title}" is overdue'
            days_overdue = (datetime.utcnow() - loan.due_at).days
            body = EmailService._generate_overdue_email(loan, days_overdue)
        
        success = EmailService.send_email(
            to=borrower.email,
            subject=subject,
            body_text=body
        )
        
        return success
    
    @staticmethod
    def _generate_before_due_email(loan, days_until):
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
```

### app/services/scheduler.py

```python
from flask import current_app
from app import db
from app.models import Loan, Notification
from app.services.email import EmailService
from datetime import datetime, timedelta


class ReminderScheduler:
    
    @staticmethod
    def process_reminders():
        current_app.logger.info('Processing reminders...')
        
        days_before = current_app.config.get('REMINDER_BEFORE_DUE', 3)
        days_after = current_app.config.get('REMINDER_AFTER_DUE', 3)
        
        stats = {
            'before_due': 0,
            'on_due': 0,
            'after_due': 0,
            'failed': 0
        }
        
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
        needed = []
        now = datetime.utcnow()
        
        before_due_date = loan.due_at - timedelta(days=days_before)
        on_due_date = loan.due_at
        after_due_date = loan.due_at + timedelta(days=days_after)
        
        if (now.date() >= before_due_date.date() and 
            now.date() < on_due_date.date()):
            if not ReminderScheduler._notification_sent(loan, 'before_due'):
                needed.append('before_due')
        
        if now.date() == on_due_date.date():
            if not ReminderScheduler._notification_sent(loan, 'on_due'):
                needed.append('on_due')
        
        if now.date() >= after_due_date.date():
            if not ReminderScheduler._notification_sent(loan, 'after_due'):
                needed.append('after_due')
        
        return needed
    
    @staticmethod
    def _notification_sent(loan, kind):
        existing = Notification.query.filter_by(
            loan_id=loan.id,
            kind=kind,
            status='sent'
        ).first()
        
        return existing is not None
    
    @staticmethod
    def _send_reminder(loan, notification_type):
        success = EmailService.send_reminder(loan, notification_type)
        
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
```

## Utilities

### app/utils/cli.py

```python
import click
from flask import current_app
from app import db


def register_commands(app):
    
    @app.cli.command('init-db')
    def init_db():
        db.create_all()
        click.echo('Database initialized.')
    
    @app.cli.command('seed-db')
    @click.option('--books', default=1000, help='Number of books to seed')
    @click.option('--borrowers', default=50, help='Number of borrowers to seed')
    @click.option('--loans', default=200, help='Number of loans to seed')
    def seed_db(books, borrowers, loans):
        from scripts.seed import seed_data
        seed_data(books, borrowers, loans)
        click.echo(f'Database seeded with {books} books, {borrowers} borrowers, {loans} loans.')
    
    @app.cli.command('rebuild-recs')
    def rebuild_recs():
        from app.services.recommendations import rebuild_recommendation_cache
        click.echo('Rebuilding recommendation cache...')
        engine = rebuild_recommendation_cache()
        click.echo(f'✓ Built model with {len(engine.book_ids)} books and {engine.tfidf_matrix.shape[1]} features')
        click.echo('✓ Cache saved to disk')
    
    @app.cli.command('test-email')
    def test_email():
        from app.services.email import EmailService
        click.echo('Testing email configuration...')
        success = EmailService.test_email_config()
        if success:
            click.echo('✓ Email test successful!')
        else:
            click.echo('✗ Email test failed. Check your SMTP settings in .env')
    
    @app.cli.command('send-reminders')
    def send_reminders_cli():
        from app.services.scheduler import ReminderScheduler
        click.echo('Processing reminders...')
        stats = ReminderScheduler.process_reminders()
        click.echo(f"✓ Sent {stats['before_due']} before-due reminders")
        click.echo(f"✓ Sent {stats['on_due']} on-due reminders")
        click.echo(f"✓ Sent {stats['after_due']} overdue reminders")
        if stats['failed'] > 0:
            click.echo(f"✗ {stats['failed']} reminders failed", err=True)
```

### app/utils/scheduler_config.py

```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import current_app


scheduler = None


def init_scheduler(app):
    global scheduler
    
    if scheduler is not None:
        return scheduler
    
    scheduler = BackgroundScheduler()
    
    scheduler.add_job(
        func=process_reminders_job,
        trigger=CronTrigger(hour=9, minute=0),
        id='process_reminders',
        name='Process loan reminders',
        replace_existing=True
    )
    
    scheduler.start()
    app.logger.info('APScheduler started')
    
    import atexit
    atexit.register(lambda: scheduler.shutdown())
    
    return scheduler


def process_reminders_job():
    from app import create_app
    from app.services.scheduler import ReminderScheduler
    
    app = create_app()
    
    with app.app_context():
        try:
            stats = ReminderScheduler.process_reminders()
            app.logger.info(f'Reminder job completed: {stats}')
        except Exception as e:
            app.logger.error(f'Reminder job failed: {e}')


def run_reminders_now():
    from app.services.scheduler import ReminderScheduler
    
    try:
        stats = ReminderScheduler.process_reminders()
        current_app.logger.info(f'Manual reminder run completed: {stats}')
        return stats
    except Exception as e:
        current_app.logger.error(f'Manual reminder run failed: {e}')
        raise
```
