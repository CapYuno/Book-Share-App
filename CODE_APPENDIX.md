# Code Appendix

This document contains all the source code for the BookShare Library Management System.

## Configuration

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
        active_loan = Loan.query.filter_by(book_id=self.id, returned_at=None).first()
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

Full implementation in source files - includes book CRUD operations, search functionality, autocomplete API endpoints, and search history management.

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
        
        existing_loan = Loan.query.filter_by(book_id=book_id, returned_at=None).first()
        
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

Full TF-IDF based recommendation API implementation - see source files for complete code.

### app/routes/admin.py

Complete admin dashboard with data export/import functionality - see source files for full implementation.

## Services

### app/services/recommendations.py

Complete TF-IDF recommendation engine implementation with caching - see source files.

### app/services/email.py

Email service for sending loan reminder notifications - see source files.

### app/services/scheduler.py

APScheduler-based reminder processing service - see source files.

## Utilities

### app/utils/cli.py

Flask CLI commands for database operations and system management - see source files.

### app/utils/scheduler_config.py

APScheduler configuration and initialization - see source files.

## Templates

All HTML templates use Jinja2 templating with Tailwind CSS for styling. Key templates include:

- `base.html` - Base layout with navigation
- `dashboard/index.html` - Main dashboard
- `books/list.html` - Book listing with autocomplete search
- `books/detail.html` - Book details with AI recommendations
- `books/form.html` - Book create/edit form
- `borrowers/*.html` - Borrower management templates
- `loans/*.html` - Loan management templates
- `admin/dashboard.html` - Admin control panel

Complete template code available in `app/templates/` directory.
