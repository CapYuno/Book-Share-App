"""AI-powered book recommendation service using TF-IDF content-based filtering."""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.models import Book
from flask import current_app
import pickle
import os


class RecommendationEngine:
    """Content-based recommendation engine using TF-IDF."""
    
    def __init__(self):
        """Initialize the recommendation engine."""
        self.vectorizer = None
        self.tfidf_matrix = None
        self.book_ids = []
        self.is_fitted = False
        
    def _prepare_features(self, book):
        """Prepare feature text from book attributes.
        
        Args:
            book: Book model instance
            
        Returns:
            Combined text string for vectorization
        """
        # Combine title, author, genre, and description
        # Weight title and author more heavily by repeating them
        features = []
        
        if book.title:
            features.append(book.title.lower())
            features.append(book.title.lower())  # Repeat for higher weight
        
        if book.author:
            features.append(book.author.lower())
            features.append(book.author.lower())  # Repeat for higher weight
        
        if book.genre:
            features.append(book.genre.lower())
            features.append(book.genre.lower())
            features.append(book.genre.lower())  # Triple weight for genre
        
        if book.description:
            features.append(book.description.lower())
        
        return ' '.join(features)
    
    def build_model(self, books=None):
        """Build TF-IDF model from all books.
        
        Args:
            books: Optional list of books. If None, fetches all from database.
        """
        if books is None:
            books = Book.query.all()
        
        if not books:
            current_app.logger.warning('No books available to build recommendation model')
            return
        
        # Prepare feature texts
        feature_texts = []
        self.book_ids = []
        
        for book in books:
            feature_texts.append(self._prepare_features(book))
            self.book_ids.append(book.id)
        
        # Configure TF-IDF vectorizer
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
        
        # Fit and transform
        self.tfidf_matrix = self.vectorizer.fit_transform(feature_texts)
        self.is_fitted = True
        
        current_app.logger.info(
            f'Built TF-IDF model: {len(books)} books, '
            f'{self.tfidf_matrix.shape[1]} features'
        )
    
    def get_recommendations(self, book_id, top_k=3):
        """Get top-K similar books for a given book.
        
        Args:
            book_id: ID of the book to find recommendations for
            top_k: Number of recommendations to return
            
        Returns:
            List of tuples (book_id, similarity_score)
        """
        if not self.is_fitted:
            current_app.logger.warning('Model not fitted, building now...')
            self.build_model()
        
        # Find index of the book
        try:
            book_idx = self.book_ids.index(book_id)
        except ValueError:
            current_app.logger.error(f'Book {book_id} not found in model')
            return []
        
        # Calculate cosine similarity with all other books
        book_vector = self.tfidf_matrix[book_idx]
        similarities = cosine_similarity(book_vector, self.tfidf_matrix).flatten()
        
        # Get indices of top-K similar books (excluding the book itself)
        # argsort returns indices in ascending order, so we reverse it
        similar_indices = similarities.argsort()[::-1]
        
        # Filter out the book itself and get top-K
        recommendations = []
        for idx in similar_indices:
            if self.book_ids[idx] != book_id:  # Exclude self
                recommendations.append((
                    self.book_ids[idx],
                    float(similarities[idx])
                ))
                if len(recommendations) >= top_k:
                    break
        
        return recommendations
    
    def get_recommendations_for_borrower(self, borrower_id, top_k=3):
        """Get personalized recommendations based on borrower history.
        
        Args:
            borrower_id: ID of the borrower
            top_k: Number of recommendations to return
            
        Returns:
            List of tuples (book_id, similarity_score, source_book_title)
        """
        from app.models import Loan
        
        # Get books this borrower has read (returned loans)
        past_loans = Loan.query.filter_by(
            borrower_id=borrower_id
        ).filter(
            Loan.returned_at.isnot(None)
        ).order_by(Loan.returned_at.desc()).limit(5).all()
        
        if not past_loans:
            return []
        
        # Aggregate recommendations from all past books
        all_recommendations = {}
        
        for loan in past_loans:
            book_recs = self.get_recommendations(loan.book_id, top_k=10)
            for book_id, score in book_recs:
                if book_id in all_recommendations:
                    # Average scores if book recommended multiple times
                    all_recommendations[book_id] = (
                        all_recommendations[book_id] + score
                    ) / 2
                else:
                    all_recommendations[book_id] = score
        
        # Sort by score and return top-K
        sorted_recs = sorted(
            all_recommendations.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]
        
        return [(book_id, score, None) for book_id, score in sorted_recs]
    
    def save_cache(self, cache_path='tfidf_cache.pkl'):
        """Save the model to disk for faster loading.
        
        Args:
            cache_path: Path to save the cache file
        """
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
        """Load the model from disk.
        
        Args:
            cache_path: Path to the cache file
            
        Returns:
            True if loaded successfully, False otherwise
        """
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


# Global instance
_recommendation_engine = None


def get_recommendation_engine():
    """Get or create the global recommendation engine instance.
    
    Returns:
        RecommendationEngine instance
    """
    global _recommendation_engine
    
    if _recommendation_engine is None:
        _recommendation_engine = RecommendationEngine()
        
        # Try to load from cache, otherwise build new
        cache_path = current_app.config.get(
            'RECOMMENDATION_CACHE_PATH',
            'tfidf_cache.pkl'
        )
        
        if not _recommendation_engine.load_cache(cache_path):
            current_app.logger.info('Building new recommendation model...')
            _recommendation_engine.build_model()
    
    return _recommendation_engine


def rebuild_recommendation_cache():
    """Rebuild the recommendation cache from scratch.
    
    This should be called when books are added/updated/deleted.
    """
    global _recommendation_engine
    
    engine = RecommendationEngine()
    engine.build_model()
    
    cache_path = current_app.config.get(
        'RECOMMENDATION_CACHE_PATH',
        'tfidf_cache.pkl'
    )
    engine.save_cache(cache_path)
    
    # Update global instance
    _recommendation_engine = engine
    
    return engine
