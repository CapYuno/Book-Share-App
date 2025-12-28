"""Unit tests for Book model."""
from app.models import Book, Loan
from datetime import datetime, timedelta


def test_book_creation(db):
    """Test creating a book."""
    book = Book(
        title='1984',
        author='George Orwell',
        isbn='9780451524935',
        year=1949,
        genre='Fiction'
    )
    db.session.add(book)
    db.session.commit()
    
    assert book.id is not None
    assert book.title == '1984'
    assert book.author == 'George Orwell'


def test_book_to_dict(sample_book):
    """Test book serialization."""
    book_dict = sample_book.to_dict()
    
    assert book_dict['title'] == 'Test Book'
    assert book_dict['author'] == 'Test Author'
    assert 'id' in book_dict


def test_book_is_available(db, sample_book, sample_borrower):
    """Test book availability check."""
    # Book should be available initially
    assert sample_book.is_available is True
    
    # Create active loan
    loan = Loan(
        book_id=sample_book.id,
        borrower_id=sample_borrower.id,
        due_at=datetime.utcnow() + timedelta(days=14)
    )
    db.session.add(loan)
    db.session.commit()
    
    # Book should not be available now
    assert sample_book.is_available is False
    
    # Return the book
    loan.returned_at = datetime.utcnow()
    db.session.commit()
    
    # Book should be available again
    assert sample_book.is_available is True
