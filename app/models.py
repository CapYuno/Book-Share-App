"""Database models for BookShare application."""
from datetime import datetime
from app import db


class Book(db.Model):
    """Book model for library inventory."""
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    author = db.Column(db.String(200), nullable=False, index=True)
    isbn = db.Column(db.String(13), unique=True, index=True)
    year = db.Column(db.Integer)
    genre = db.Column(db.String(100), index=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    loans = db.relationship('Loan', backref='book', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Book {self.title} by {self.author}>'
    
    def to_dict(self):
        """Convert book to dictionary."""
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
        """Check if book is currently available (not on loan)."""
        active_loan = Loan.query.filter_by(
            book_id=self.id,
            returned_at=None
        ).first()
        return active_loan is None


class Borrower(db.Model):
    """Borrower/patron model."""
    __tablename__ = 'borrowers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    email = db.Column(db.String(200), nullable=False, unique=True, index=True)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    loans = db.relationship('Loan', backref='borrower', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Borrower {self.name}>'
    
    def to_dict(self):
        """Convert borrower to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Loan(db.Model):
    """Loan transaction model."""
    __tablename__ = 'loans'
    
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False, index=True)
    borrower_id = db.Column(db.Integer, db.ForeignKey('borrowers.id'), nullable=False, index=True)
    loaned_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    due_at = db.Column(db.DateTime, nullable=False, index=True)
    returned_at = db.Column(db.DateTime)
    
    # Relationships
    notifications = db.relationship('Notification', backref='loan', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Loan book_id={self.book_id} borrower_id={self.borrower_id}>'
    
    def to_dict(self):
        """Convert loan to dictionary."""
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
        """Check if loan is overdue."""
        if self.returned_at:
            return False
        return datetime.utcnow() > self.due_at


class Notification(db.Model):
    """Email notification tracking."""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('loans.id'), nullable=False, index=True)
    kind = db.Column(db.String(50), nullable=False)  # 'before_due', 'on_due', 'after_due'
    scheduled_at = db.Column(db.DateTime, nullable=False, index=True)
    sent_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'sent', 'failed'
    
    def __repr__(self):
        return f'<Notification loan_id={self.loan_id} kind={self.kind}>'
    
    def to_dict(self):
        """Convert notification to dictionary."""
        return {
            'id': self.id,
            'loan_id': self.loan_id,
            'kind': self.kind,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'status': self.status
        }


class Setting(db.Model):
    """Application settings key-value store."""
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Setting {self.key}={self.value}>'
    
    @staticmethod
    def get_value(key, default=None):
        """Get setting value by key."""
        setting = Setting.query.filter_by(key=key).first()
        return setting.value if setting else default
    
    @staticmethod
    def set_value(key, value):
        """Set setting value by key."""
        setting = Setting.query.filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            setting = Setting(key=key, value=value)
            db.session.add(setting)
        db.session.commit()
