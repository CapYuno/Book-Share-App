"""Unit tests for AI recommendation engine."""
from app.models import Book
from app.services.recommendations import RecommendationEngine
import time


def test_recommendation_engine_build(db):
    """Test building the TF-IDF model."""
    # Create some test books
    books = [
        Book(
            title='The Great Gatsby',
            author='F. Scott Fitzgerald',
            genre='Fiction',
            description='A classic American novel about the Jazz Age'
        ),
        Book(
            title='To Kill a Mockingbird',
            author='Harper Lee',
            genre='Fiction',
            description='A gripping tale of racial injustice and childhood innocence'
        ),
        Book(
            title='1984',
            author='George Orwell',
            genre='Science Fiction',
            description='A dystopian social science fiction novel'
        ),
        Book(
            title='Animal Farm',
            author='George Orwell',
            genre='Fiction',
            description='A political satire about farm animals'
        )
    ]
    
    for book in books:
        db.session.add(book)
    db.session.commit()
    
    # Build recommendation engine
    engine = RecommendationEngine()
    engine.build_model(books)
    
    # Verify model is fitted
    assert engine.is_fitted is True
    assert len(engine.book_ids) == 4
    assert engine.tfidf_matrix is not None
    assert engine.vectorizer is not None


def test_get_recommendations(db):
    """Test getting book recommendations."""
    # Create test books
    books = [
        Book(
            id=1,
            title='Harry Potter and the Philosopher Stone',
            author='J.K. Rowling',
            genre='Fantasy',
            description='A young wizard discovers his magical heritage'
        ),
        Book(
            id=2,
            title='Harry Potter and the Chamber of Secrets',
            author='J.K. Rowling',
            genre='Fantasy',
            description='Harry returns to Hogwarts for his second year'
        ),
        Book(
            id=3,
            title='The Hobbit',
            author='J.R.R. Tolkien',
            genre='Fantasy',
            description='A hobbit goes on an unexpected journey'
        ),
        Book(
            id=4,
            title='Clean Code',
            author='Robert Martin',
            genre='Technology',
            description='A handbook of agile software craftsmanship'
        )
    ]
    
    for book in books:
        db.session.add(book)
    db.session.commit()
    
    # Build engine
    engine = RecommendationEngine()
    engine.build_model(books)
    
    # Get recommendations for first Harry Potter book
    recommendations = engine.get_recommendations(1, top_k=2)
    
    # Should have recommendations
    assert len(recommendations) > 0
    assert len(recommendations) <= 2
    
    # Verify format: list of (book_id, similarity_score)
    for book_id, score in recommendations:
        assert isinstance(book_id, int)
        assert isinstance(score, float)
        assert 0 <= score <= 1
        assert book_id != 1  # Should not recommend itself


def test_recommendations_exclude_self(db):
    """Test that recommendations don't include the source book."""
    books = [
        Book(title='Book A', author='Author X', genre='Fiction'),
        Book(title='Book B', author='Author X', genre='Fiction'),
        Book(title='Book C', author='Author Y', genre='Fiction')
    ]
    
    for book in books:
        db.session.add(book)
    db.session.commit()
    
    engine = RecommendationEngine()
    engine.build_model(books)
    
    # Get recommendations for first book
    book_id = books[0].id
    recommendations = engine.get_recommendations(book_id, top_k=5)
    
    # Verify source book is not in recommendations
    recommended_ids = [rec_id for rec_id, score in recommendations]
    assert book_id not in recommended_ids


def test_similar_books_score_higher(db):
    """Test that similar books get higher similarity scores."""
    books = [
        Book(
            title='Python Programming',
            author='John Doe',
            genre='Technology',
            description='Learn Python programming from scratch'
        ),
        Book(
            title='Advanced Python',
            author='Jane Smith',
            genre='Technology',
            description='Advanced Python programming techniques'
        ),
        Book(
            title='Cooking Basics',
            author='Chef Mike',
            genre='Cooking',
            description='Learn how to cook delicious meals'
        )
    ]
    
    for book in books:
        db.session.add(book)
    db.session.commit()
    
    engine = RecommendationEngine()
    engine.build_model(books)
    
    # Get recommendations for first Python book
    recommendations = engine.get_recommendations(books[0].id, top_k=2)
    
    # The second Python book should have higher similarity than cooking book
    # (assuming it's in the recommendations)
    if len(recommendations) >= 2:
        python_book_id = books[1].id
        cooking_book_id = books[2].id
        
        rec_dict = dict(recommendations)
        
        # If both are recommended, Python book should have higher score
        if python_book_id in rec_dict and cooking_book_id in rec_dict:
            assert rec_dict[python_book_id] > rec_dict[cooking_book_id]


def test_recommendation_performance(db):
    """Test that recommendations are computed quickly."""
    # Create 100 books
    books = []
    for i in range(100):
        books.append(Book(
            title=f'Book {i}',
            author=f'Author {i % 10}',
            genre=['Fiction', 'Science Fiction', 'Fantasy'][i % 3],
            description=f'This is a book about topic {i % 20}'
        ))
    
    for book in books:
        db.session.add(book)
    db.session.commit()
    
    # Build engine
    engine = RecommendationEngine()
    
    # Time the model building
    start = time.time()
    engine.build_model(books)
    build_time = (time.time() - start) * 1000
    
    # Should build in reasonable time (< 2 seconds for 100 books)
    assert build_time < 2000, f"Model building too slow: {build_time}ms"
    
    # Time recommendation computation
    start = time.time()
    recommendations = engine.get_recommendations(books[0].id, top_k=3)
    rec_time = (time.time() - start) * 1000
    
    # Should compute recommendations quickly (< 100ms)
    assert rec_time < 100, f"Recommendation too slow: {rec_time}ms"
    
    # Verify we got recommendations
    assert len(recommendations) == 3
