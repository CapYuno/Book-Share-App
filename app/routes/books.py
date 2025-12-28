"""Books blueprint."""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from app import db
from app.models import Book
from sqlalchemy import or_

bp = Blueprint('books', __name__, url_prefix='/books')


@bp.route('/')
def list_books():
    """List all books with optional search."""
    query = request.args.get('q', '')
    
    if query:
        books = Book.query.filter(
            or_(
                Book.title.ilike(f'%{query}%'),
                Book.author.ilike(f'%{query}%'),
                Book.isbn.ilike(f'%{query}%'),
                Book.genre.ilike(f'%{query}%')
            )
        ).all()
    else:
        books = Book.query.all()
    
    return render_template('books/list.html', books=books, query=query)


@bp.route('/<int:book_id>')
def detail(book_id):
    """Book detail page."""
    book = Book.query.get_or_404(book_id)
    return render_template('books/detail.html', book=book)


@bp.route('/new', methods=['GET', 'POST'])
def create():
    """Create a new book."""
    if request.method == 'POST':
        # Validate and sanitize inputs
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        isbn = request.form.get('isbn', '').strip() or None
        genre = request.form.get('genre', '').strip() or None
        description = request.form.get('description', '').strip() or None
        
        # Validate required fields
        if not title or not author:
            flash('Title and Author are required fields!', 'error')
            return render_template('books/form.html', book=None)
        
        # Limit lengths for security
        if len(title) > 200:
            flash('Title must be 200 characters or less!', 'error')
            return render_template('books/form.html', book=None)
        
        if len(author) > 200:
            flash('Author must be 200 characters or less!', 'error')
            return render_template('books/form.html', book=None)
        
        if description and len(description) > 2000:
            flash('Description must be 2000 characters or less!', 'error')
            return render_template('books/form.html', book=None)
        
        book = Book(
            title=title,
            author=author,
            isbn=isbn,
            year=request.form.get('year', type=int),
            genre=genre,
            description=description
        )
        db.session.add(book)
        db.session.commit()
        
        # Rebuild recommendation cache in background
        try:
            from app.services.recommendations import rebuild_recommendation_cache
            rebuild_recommendation_cache()
            current_app.logger.info('Recommendation cache rebuilt after book creation')
        except Exception as e:
            current_app.logger.error(f'Failed to rebuild recommendation cache: {e}')
        
        flash('Book created successfully!', 'success')
        return redirect(url_for('books.detail', book_id=book.id))
    
    return render_template('books/form.html', book=None)



@bp.route('/<int:book_id>/edit', methods=['GET', 'POST'])
def edit(book_id):
    """Edit a book."""
    book = Book.query.get_or_404(book_id)
    
    if request.method == 'POST':
        book.title = request.form['title']
        book.author = request.form['author']
        book.isbn = request.form.get('isbn')
        book.year = request.form.get('year', type=int)
        book.genre = request.form.get('genre')
        book.description = request.form.get('description')
        db.session.commit()
        
        # Rebuild recommendation cache in background
        try:
            from app.services.recommendations import rebuild_recommendation_cache
            rebuild_recommendation_cache()
            current_app.logger.info('Recommendation cache rebuilt after book update')
        except Exception as e:
            current_app.logger.error(f'Failed to rebuild recommendation cache: {e}')
        
        flash('Book updated successfully!', 'success')
        return redirect(url_for('books.detail', book_id=book.id))
    
    return render_template('books/form.html', book=book)


@bp.route('/<int:book_id>/delete', methods=['POST'])
def delete(book_id):
    """Delete a book."""
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    
    # Rebuild recommendation cache in background
    try:
        from app.services.recommendations import rebuild_recommendation_cache
        rebuild_recommendation_cache()
        current_app.logger.info('Recommendation cache rebuilt after book deletion')
    except Exception as e:
        current_app.logger.error(f'Failed to rebuild recommendation cache: {e}')
    
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('books.list_books'))


# API endpoints for AJAX
@bp.route('/api/search')
def api_search():
    """Search books API endpoint."""
    query = request.args.get('q', '')
    
    books = Book.query.filter(
        or_(
            Book.title.ilike(f'%{query}%'),
            Book.author.ilike(f'%{query}%'),
            Book.isbn.ilike(f'%{query}%')
        )
    ).limit(10).all()
    
    return jsonify([book.to_dict() for book in books])


@bp.route('/api/autocomplete')
def api_autocomplete():
    """Autocomplete API endpoint with search history and live results."""
    from flask import session
    
    query = request.args.get('q', '').strip()
    
    # Get search history from session
    search_history = session.get('book_search_history', [])
    
    # Get matching books if query is provided
    results = []
    if query:
        books = Book.query.filter(
            or_(
                Book.title.ilike(f'%{query}%'),
                Book.author.ilike(f'%{query}%'),
                Book.genre.ilike(f'%{query}%')
            )
        ).limit(8).all()
        
        results = [{
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'genre': book.genre,
            'is_available': book.is_available
        } for book in books]
    
    return jsonify({
        'history': search_history[-5:],  # Last 5 searches
        'results': results
    })


@bp.route('/api/history', methods=['POST'])
def api_save_history():
    """Save search query to history."""
    from flask import session
    
    data = request.get_json()
    query = data.get('query', '').strip()
    
    if query:
        # Initialize history if not exists
        if 'book_search_history' not in session:
            session['book_search_history'] = []
        
        history = session['book_search_history']
        
        # Remove duplicate if exists
        if query in history:
            history.remove(query)
        
        # Add to front of history
        history.insert(0, query)
        
        # Keep only last 10 searches
        session['book_search_history'] = history[:10]
        
        # Mark session as modified
        session.modified = True
    
    return jsonify({'success': True})


@bp.route('/api/history', methods=['DELETE'])
def api_clear_history():
    """Clear search history."""
    from flask import session
    
    session.pop('book_search_history', None)
    session.modified = True
    
    return jsonify({'success': True})
