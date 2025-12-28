"""Pytest configuration."""
import pytest
from app import create_app, db as _db
from app.models import Book, Borrower, Loan


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    app = create_app('testing')
    return app


@pytest.fixture(scope='function')
def db(app):
    """Create database for testing."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def sample_book(db):
    """Create a sample book for testing."""
    book = Book(
        title='Test Book',
        author='Test Author',
        isbn='9781234567890',
        year=2020,
        genre='Fiction',
        description='A test book for unit testing'
    )
    db.session.add(book)
    db.session.commit()
    return book


@pytest.fixture
def sample_borrower(db):
    """Create a sample borrower for testing."""
    borrower = Borrower(
        name='Test Borrower',
        email='test@example.com',
        phone='1234567890'
    )
    db.session.add(borrower)
    db.session.commit()
    return borrower
