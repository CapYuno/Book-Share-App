from app.models import Book
from flask import current_app
from collections import Counter


class RecommendationEngine:
    
    def __init__(self):
        self.is_fitted = True
    
    def _get_keywords(self, book):
        keywords = []
        
        if book.genre:
            keywords.extend(book.genre.lower().split())
        
        if book.title:
            title_words = [w.lower() for w in book.title.split() if len(w) > 3]
            keywords.extend(title_words[:3])
        
        if book.author:
            keywords.append(book.author.lower())
        
        if book.description:
            desc_words = [w.lower() for w in book.description.split() if len(w) > 5]
            keywords.extend(desc_words[:5])
        
        return keywords
    
    def get_recommendations(self, book_id, top_k=3):
        book = Book.query.get(book_id)
        if not book:
            return []
        
        book_keywords = set(self._get_keywords(book))
        
        all_books = Book.query.filter(Book.id != book_id).all()
        
        scored_books = []
        for other_book in all_books:
            other_keywords = set(self._get_keywords(other_book))
            
            score = 0
            
            if book.genre and other_book.genre and book.genre.lower() == other_book.genre.lower():
                score += 10
            
            common_keywords = book_keywords & other_keywords
            score += len(common_keywords) * 2
            
            if book.author and other_book.author and book.author.lower() == other_book.author.lower():
                score += 5
            
            if score > 0:
                scored_books.append((other_book.id, score / 20.0))
        
        scored_books.sort(key=lambda x: x[1], reverse=True)
        
        return scored_books[:top_k]
    
    def get_recommendations_for_borrower(self, borrower_id, top_k=3):
        from app.models import Loan
        
        past_loans = Loan.query.filter_by(
            borrower_id=borrower_id
        ).filter(
            Loan.returned_at.isnot(None)
        ).order_by(Loan.returned_at.desc()).limit(5).all()
        
        if not past_loans:
            return []
        
        genre_counter = Counter()
        author_counter = Counter()
        
        for loan in past_loans:
            if loan.book.genre:
                genre_counter[loan.book.genre.lower()] += 1
            if loan.book.author:
                author_counter[loan.book.author.lower()] += 1
        
        all_books = Book.query.all()
        
        scored_books = []
        for book in all_books:
            if any(loan.book_id == book.id for loan in past_loans):
                continue
            
            score = 0
            
            if book.genre:
                score += genre_counter.get(book.genre.lower(), 0) * 5
            
            if book.author:
                score += author_counter.get(book.author.lower(), 0) * 3
            
            if score > 0:
                scored_books.append((book.id, score / 20.0, None))
        
        scored_books.sort(key=lambda x: x[1], reverse=True)
        
        return scored_books[:top_k]
    
    def build_model(self, books=None):
        pass
    
    def save_cache(self, cache_path='recommendations_cache.pkl'):
        pass
    
    def load_cache(self, cache_path='recommendations_cache.pkl'):
        return True


_recommendation_engine = None


def get_recommendation_engine():
    global _recommendation_engine
    
    if _recommendation_engine is None:
        _recommendation_engine = RecommendationEngine()
    
    return _recommendation_engine


def rebuild_recommendation_cache():
    global _recommendation_engine
    _recommendation_engine = RecommendationEngine()
    return _recommendation_engine
