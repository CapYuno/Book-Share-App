"""Recommendations blueprint - AI-powered book recommendations."""
from flask import Blueprint, jsonify, request, current_app
from app.models import Book, Borrower
from app.services.recommendations import get_recommendation_engine
import time

bp = Blueprint('recommendations', __name__, url_prefix='/recommendations')


@bp.route('/books/<int:book_id>')
def get_recommendations(book_id):
    """Get AI-powered book recommendations using TF-IDF content-based filtering.
    
    Args:
        book_id: ID of the book to get recommendations for
        
    Query params:
        top: Number of recommendations (default: from config)
        
    Returns:
        JSON with recommendations and timing metrics
    """
    start_time = time.time()
    
    # Verify book exists
    book = Book.query.get_or_404(book_id)
    
    # Get top_k from query params or config
    top_k = request.args.get('top', type=int) or \
            current_app.config.get('RECOMMENDATIONS_TOP_K', 3)
    
    # Get recommendation engine and compute recommendations
    engine = get_recommendation_engine()
    recommendations = engine.get_recommendations(book_id, top_k=top_k)
    
    # Fetch book details for recommendations
    recommended_books = []
    for rec_book_id, similarity_score in recommendations:
        rec_book = Book.query.get(rec_book_id)
        if rec_book:
            book_data = rec_book.to_dict()
            book_data['similarity_score'] = round(similarity_score, 4)
            recommended_books.append(book_data)
    
    # Calculate latency
    latency_ms = (time.time() - start_time) * 1000
    
    return jsonify({
        'book_id': book_id,
        'book_title': book.title,
        'recommendations': recommended_books,
        'count': len(recommended_books),
        'latency_ms': round(latency_ms, 2),
        'algorithm': 'Genre & Keyword Matching'
    })


@bp.route('/borrowers/<int:borrower_id>')
def get_borrower_recommendations(borrower_id):
    """Get personalized recommendations based on borrower's reading history.
    
    Args:
        borrower_id: ID of the borrower
        
    Returns:
        JSON with personalized recommendations
    """
    start_time = time.time()
    
    # Verify borrower exists
    borrower = Borrower.query.get_or_404(borrower_id)
    
    # Get top_k from query params or config
    top_k = request.args.get('top', type=int) or \
            current_app.config.get('RECOMMENDATIONS_TOP_K', 3)
    
    # Get personalized recommendations
    engine = get_recommendation_engine()
    recommendations = engine.get_recommendations_for_borrower(borrower_id, top_k=top_k)
    
    # Fetch book details
    recommended_books = []
    for rec_book_id, similarity_score, source in recommendations:
        rec_book = Book.query.get(rec_book_id)
        if rec_book:
            book_data = rec_book.to_dict()
            book_data['similarity_score'] = round(similarity_score, 4)
            recommended_books.append(book_data)
    
    # Calculate latency
    latency_ms = (time.time() - start_time) * 1000
    
    return jsonify({
        'borrower_id': borrower_id,
        'borrower_name': borrower.name,
        'recommendations': recommended_books,
        'count': len(recommended_books),
        'latency_ms': round(latency_ms, 2),
        'algorithm': 'Genre & Keyword Matching (History-Based)'
    })


@bp.route('/rebuild', methods=['POST'])
def rebuild_cache():
    """Manually rebuild the recommendation cache.
    
    This should be called when books are added/updated in bulk.
    """
    from app.services.recommendations import rebuild_recommendation_cache
    
    start_time = time.time()
    engine = rebuild_recommendation_cache()
    latency_ms = (time.time() - start_time) * 1000
    
    return jsonify({
        'status': 'success',
        'message': 'Recommendation engine reinitialized',
        'algorithm': 'Genre & Keyword Matching',
        'rebuild_time_ms': round(latency_ms, 2)
    })
