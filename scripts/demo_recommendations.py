"""Demo script to test AI recommendations."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Book
from app.services.recommendations import get_recommendation_engine
import time


def demo_recommendations():
    """Demonstrate the AI recommendation system."""
    app = create_app('development')
    
    with app.app_context():
        print("=" * 70)
        print("🤖 BookShare AI Recommendation System Demo")
        print("=" * 70)
        print()
        
        # Get total book count
        total_books = Book.query.count()
        print(f"📚 Total books in library: {total_books}")
        print()
        
        if total_books == 0:
            print("⚠️  No books found. Please run: flask seed-db")
            return
        
        # Get recommendation engine
        print("⚙️  Building TF-IDF model...")
        start_time = time.time()
        engine = get_recommendation_engine()
        build_time = (time.time() - start_time) * 1000
        
        print(f"✓ Model built in {build_time:.2f}ms")
        print(f"✓ Vocabulary size: {engine.tfidf_matrix.shape[1]} features")
        print()
        
        # Pick a random book
        sample_book = Book.query.first()
        
        print(f"📖 Sample Book:")
        print(f"   Title: {sample_book.title}")
        print(f"   Author: {sample_book.author}")
        print(f"   Genre: {sample_book.genre or 'N/A'}")
        if sample_book.description:
            desc = sample_book.description[:100] + "..." if len(sample_book.description) > 100 else sample_book.description
            print(f"   Description: {desc}")
        print()
        
        # Get recommendations
        print("🔍 Computing recommendations...")
        start_time = time.time()
        recommendations = engine.get_recommendations(sample_book.id, top_k=5)
        rec_time = (time.time() - start_time) * 1000
        
        print(f"✓ Recommendations computed in {rec_time:.2f}ms")
        print()
        
        # Display recommendations
        if recommendations:
            print("🎯 Top 5 Recommended Books:")
            print("-" * 70)
            for i, (book_id, similarity) in enumerate(recommendations, 1):
                rec_book = Book.query.get(book_id)
                similarity_percent = similarity * 100
                
                print(f"\n{i}. {rec_book.title}")
                print(f"   Author: {rec_book.author}")
                print(f"   Genre: {rec_book.genre or 'N/A'}")
                print(f"   Similarity: {similarity_percent:.1f}%")
                print(f"   Match: {'⭐' * int(similarity_percent / 20)}")
        else:
            print("❌ No recommendations found")
        
        print()
        print("=" * 70)
        print("✅ Demo completed!")
        print()
        print("💡 Try it yourself:")
        print("   1. Start the app: python run.py")
        print("   2. Visit: http://localhost:5000/books")
        print("   3. Click on any book to see AI recommendations")
        print()
        print("📊 API Endpoints:")
        print("   • GET /recommendations/books/<id>")
        print("   • GET /recommendations/borrowers/<id>")
        print("   • POST /recommendations/rebuild")
        print("=" * 70)


if __name__ == '__main__':
    demo_recommendations()
