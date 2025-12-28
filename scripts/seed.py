"""Seed script to generate synthetic data for BookShare."""
from faker import Faker
from datetime import datetime, timedelta
import random
from app import db
from app.models import Book, Borrower, Loan

fake = Faker()

# Sample genres for books
GENRES = [
    'Fiction', 'Non-Fiction', 'Science Fiction', 'Fantasy', 'Mystery', 
    'Thriller', 'Romance', 'Historical', 'Biography', 'Self-Help',
    'Technology', 'Science', 'Philosophy', 'Poetry', 'Drama'
]


def generate_isbn():
    """Generate a fake ISBN-13."""
    return '978' + ''.join([str(random.randint(0, 9)) for _ in range(10)])


def generate_book():
    """Generate a synthetic book."""
    return Book(
        title=fake.catch_phrase().title(),
        author=fake.name(),
        isbn=generate_isbn(),
        year=random.randint(1950, 2024),
        genre=random.choice(GENRES),
        description=fake.paragraph(nb_sentences=5)
    )


def generate_borrower():
    """Generate a synthetic borrower."""
    return Borrower(
        name=fake.name(),
        email=fake.email(),
        phone=fake.phone_number()
    )


def generate_loan(book_id, borrower_id, status='active'):
    """Generate a synthetic loan.
    
    Args:
        book_id: ID of the book to loan
        borrower_id: ID of the borrower
        status: 'active', 'returned', or 'overdue'
    """
    loaned_at = fake.date_time_between(start_date='-6M', end_date='now')
    
    if status == 'active':
        due_at = loaned_at + timedelta(days=random.randint(14, 30))
        returned_at = None
    elif status == 'overdue':
        due_at = loaned_at + timedelta(days=14)
        returned_at = None
    else:  # returned
        due_at = loaned_at + timedelta(days=random.randint(14, 30))
        returned_at = loaned_at + timedelta(days=random.randint(7, 20))
    
    return Loan(
        book_id=book_id,
        borrower_id=borrower_id,
        loaned_at=loaned_at,
        due_at=due_at,
        returned_at=returned_at
    )


def seed_data(num_books=1000, num_borrowers=50, num_loans=200):
    """Seed the database with synthetic data.
    
    Args:
        num_books: Number of books to create
        num_borrowers: Number of borrowers to create
        num_loans: Number of loans to create
    """
    print(f'Seeding {num_books} books...')
    books = [generate_book() for _ in range(num_books)]
    db.session.add_all(books)
    db.session.commit()
    
    print(f'Seeding {num_borrowers} borrowers...')
    borrowers = [generate_borrower() for _ in range(num_borrowers)]
    db.session.add_all(borrowers)
    db.session.commit()
    
    print(f'Seeding {num_loans} loans...')
    book_ids = [book.id for book in books]
    borrower_ids = [borrower.id for borrower in borrowers]
    
    # Create mix of active, returned, and overdue loans
    loans = []
    for _ in range(num_loans):
        status = random.choices(
            ['active', 'returned', 'overdue'],
            weights=[0.4, 0.5, 0.1]  # 40% active, 50% returned, 10% overdue
        )[0]
        
        loan = generate_loan(
            random.choice(book_ids),
            random.choice(borrower_ids),
            status
        )
        loans.append(loan)
    
    db.session.add_all(loans)
    db.session.commit()
    
    print('Data seeding completed!')
    print(f'Created: {num_books} books, {num_borrowers} borrowers, {num_loans} loans')


if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        seed_data()
